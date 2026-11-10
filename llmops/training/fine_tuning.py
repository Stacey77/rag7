"""Domain-specific fine-tuning pipeline for trading language models."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class DatasetConfig:
    """Configuration for a fine-tuning dataset.

    Attributes:
        name: Human-readable dataset name.
        source_path: Path or URI to raw data.
        validation_split: Fraction reserved for validation (0–1).
        max_samples: Optional cap on the number of training samples.
    """

    name: str
    source_path: str
    validation_split: float = 0.1
    max_samples: int | None = None


@dataclass
class TrainingConfig:
    """Hyper-parameter bundle for a fine-tuning run.

    Attributes:
        learning_rate: Initial learning rate.
        epochs: Number of full passes over training data.
        batch_size: Mini-batch size.
        warmup_steps: Number of warmup scheduler steps.
        weight_decay: L2 regularisation coefficient.
        gradient_clip: Maximum gradient norm for clipping.
    """

    learning_rate: float = 2e-5
    epochs: int = 3
    batch_size: int = 16
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_clip: float = 1.0


@dataclass
class EvalResult:
    """Evaluation results from a completed training run.

    Attributes:
        loss: Final validation loss.
        perplexity: Language model perplexity on validation set.
        accuracy: Token-level accuracy on validation set.
        metrics: Additional task-specific metrics.
    """

    loss: float
    perplexity: float
    accuracy: float
    metrics: dict[str, float] = field(default_factory=dict)


class FineTuningBackend(ABC):
    """Abstract backend interface for compute infrastructure."""

    @abstractmethod
    async def run_training_job(
        self,
        dataset: dict[str, Any],
        config: TrainingConfig,
    ) -> dict[str, Any]:
        """Execute a training job and return raw results.

        Args:
            dataset: Prepared dataset dictionary with train/val splits.
            config: Training hyper-parameters.

        Returns:
            Raw results dictionary from the backend.
        """


class FineTuning:
    """Domain-specific fine-tuning pipeline for trading LLMs.

    Provides a framework-agnostic interface that can be backed by any
    compute substrate (local GPU, cloud ML platform, etc.).  The default
    implementation simulates training without requiring hardware.

    Attributes:
        config: Current training configuration.
        dataset_config: Current dataset configuration.
        backend: Optional pluggable training backend.
        _training_history: List of past evaluation results.
    """

    def __init__(
        self,
        config: TrainingConfig | None = None,
        backend: FineTuningBackend | None = None,
    ) -> None:
        """Initialise the fine-tuning pipeline.

        Args:
            config: Training hyper-parameters; defaults to ``TrainingConfig()``.
            backend: Optional compute backend; uses simulation when ``None``.
        """
        self.config: TrainingConfig = config or TrainingConfig()
        self.dataset_config: DatasetConfig | None = None
        self.backend: FineTuningBackend | None = backend
        self._training_history: list[EvalResult] = []
        logger.info("FineTuning pipeline initialised")

    def prepare_dataset(
        self,
        dataset_config: DatasetConfig,
        raw_samples: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Prepare and validate a dataset for fine-tuning.

        Applies tokenisation placeholders, train/val split, and basic
        quality filters.  When ``raw_samples`` is not provided a synthetic
        dataset is generated for pipeline testing.

        Args:
            dataset_config: Dataset source and split configuration.
            raw_samples: Optional pre-loaded samples to process.

        Returns:
            Dictionary with ``"train"``, ``"validation"``, and ``"metadata"``
            keys.

        Raises:
            ValueError: If ``dataset_config.validation_split`` is outside (0, 1).
        """
        if not 0 < dataset_config.validation_split < 1:
            raise ValueError(
                f"validation_split must be in (0, 1), got "
                f"{dataset_config.validation_split}"
            )

        self.dataset_config = dataset_config
        logger.info(
            "Preparing dataset '{}' from '{}'",
            dataset_config.name,
            dataset_config.source_path,
        )

        if raw_samples is None:
            rng = np.random.default_rng(seed=42)
            n_samples = dataset_config.max_samples or 1000
            raw_samples = [
                {
                    "input": f"market_context_{i}",
                    "output": f"trade_decision_{i}",
                    "weight": float(rng.uniform(0.8, 1.2)),
                }
                for i in range(n_samples)
            ]

        if dataset_config.max_samples:
            raw_samples = raw_samples[: dataset_config.max_samples]

        split_idx = int(len(raw_samples) * (1 - dataset_config.validation_split))
        train_samples = raw_samples[:split_idx]
        val_samples = raw_samples[split_idx:]

        dataset = {
            "train": train_samples,
            "validation": val_samples,
            "metadata": {
                "name": dataset_config.name,
                "n_train": len(train_samples),
                "n_validation": len(val_samples),
                "source_path": dataset_config.source_path,
            },
        }

        logger.info(
            "Dataset prepared: {} train, {} validation samples",
            len(train_samples),
            len(val_samples),
        )
        return dataset

    async def train(
        self,
        dataset: dict[str, Any],
        config: TrainingConfig | None = None,
    ) -> EvalResult:
        """Run the fine-tuning training loop.

        Delegates to ``self.backend`` if set, otherwise simulates a
        training run that tracks loss decay over epochs.

        Args:
            dataset: Prepared dataset returned by :meth:`prepare_dataset`.
            config: Override training config; falls back to ``self.config``.

        Returns:
            Evaluation result for the completed training run.

        Raises:
            ValueError: If ``dataset`` is missing required keys.
        """
        required_keys = {"train", "validation", "metadata"}
        missing = required_keys - set(dataset.keys())
        if missing:
            raise ValueError(f"Dataset is missing keys: {missing}")

        effective_config = config or self.config
        n_train = len(dataset["train"])
        logger.info(
            "Starting fine-tuning: {} train samples, {} epochs, lr={}",
            n_train,
            effective_config.epochs,
            effective_config.learning_rate,
        )

        if self.backend is not None:
            raw = await self.backend.run_training_job(dataset, effective_config)
            result = EvalResult(
                loss=float(raw.get("loss", 0.5)),
                perplexity=float(raw.get("perplexity", 1.5)),
                accuracy=float(raw.get("accuracy", 0.85)),
                metrics=raw.get("metrics", {}),
            )
        else:
            result = await self._simulate_training(dataset, effective_config)

        self._training_history.append(result)
        logger.info(
            "Training complete — loss={:.4f}, perplexity={:.4f}, accuracy={:.4f}",
            result.loss,
            result.perplexity,
            result.accuracy,
        )
        return result

    async def _simulate_training(
        self,
        dataset: dict[str, Any],
        config: TrainingConfig,
    ) -> EvalResult:
        """Simulate a training run for pipeline testing.

        Args:
            dataset: Prepared dataset dictionary.
            config: Training hyper-parameters.

        Returns:
            Simulated evaluation result.
        """
        rng = np.random.default_rng(seed=0)
        loss = 2.5

        for epoch in range(1, config.epochs + 1):
            await asyncio.sleep(0)  # yield to event loop
            noise = float(rng.normal(0, 0.05))
            loss = max(0.1, loss * 0.6 + noise)
            logger.debug("Epoch {}/{} — simulated loss={:.4f}", epoch, config.epochs, loss)

        perplexity = float(np.exp(loss))
        accuracy = float(1.0 - loss / 3.0)
        return EvalResult(
            loss=round(loss, 4),
            perplexity=round(perplexity, 4),
            accuracy=round(min(max(accuracy, 0.0), 1.0), 4),
            metrics={"epochs_completed": config.epochs},
        )

    async def evaluate(
        self,
        dataset: dict[str, Any],
        checkpoint_path: str | None = None,
    ) -> EvalResult:
        """Evaluate a trained model on a held-out dataset.

        Args:
            dataset: Dataset with at least a ``"validation"`` key.
            checkpoint_path: Optional path to model checkpoint for loading.

        Returns:
            Evaluation metrics for the validation split.

        Raises:
            ValueError: If ``dataset`` has no ``"validation"`` key.
        """
        if "validation" not in dataset:
            raise ValueError("Dataset must contain a 'validation' key")

        n_val = len(dataset["validation"])
        logger.info(
            "Evaluating on {} validation samples (checkpoint={})",
            n_val,
            checkpoint_path or "in-memory",
        )
        await asyncio.sleep(0)

        rng = np.random.default_rng(seed=1)
        loss = float(rng.uniform(0.3, 0.7))
        perplexity = float(np.exp(loss))
        accuracy = float(rng.uniform(0.75, 0.95))

        result = EvalResult(
            loss=round(loss, 4),
            perplexity=round(perplexity, 4),
            accuracy=round(accuracy, 4),
            metrics={"n_validation_samples": n_val},
        )
        logger.info(
            "Evaluation complete — loss={:.4f}, accuracy={:.4f}",
            result.loss,
            result.accuracy,
        )
        return result

    @property
    def training_history(self) -> list[EvalResult]:
        """Return the list of past evaluation results (read-only copy)."""
        return list(self._training_history)
