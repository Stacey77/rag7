"""Continual learning: ongoing model updates without catastrophic forgetting."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class DriftSignal:
    """Result of a concept/data drift detection check.

    Attributes:
        detected: Whether drift was detected.
        drift_score: Magnitude of the drift (0 = none, 1 = severe).
        affected_features: Names of features that showed drift.
        detected_at: UTC timestamp of detection.
        method: Statistical test used (e.g. ``"psi"``, ``"ks"``).
    """

    detected: bool
    drift_score: float
    affected_features: list[str]
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    method: str = "psi"


@dataclass
class KnowledgeEntry:
    """An entry in the model knowledge base.

    Attributes:
        key: Unique knowledge identifier.
        content: Knowledge payload (e.g. updated market regime rules).
        version: Monotonically increasing version counter.
        updated_at: UTC timestamp of last update.
        confidence: Confidence weight for this knowledge entry (0–1).
    """

    key: str
    content: Any
    version: int = 1
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0


class ContinualLearning:
    """Ongoing model update framework using continual learning techniques.

    Implements experience replay and elastic weight consolidation stubs to
    allow model knowledge updates without catastrophic forgetting of
    previously learned capabilities.

    Attributes:
        knowledge_base: Current knowledge entries keyed by identifier.
        drift_history: Log of all detected drift signals.
        replay_buffer: Experience replay buffer for catastrophic forgetting
            mitigation.
        _model_version: Current model version counter.
        _psi_threshold: PSI score above which drift is declared.
    """

    def __init__(
        self,
        psi_threshold: float = 0.2,
        replay_buffer_size: int = 1000,
    ) -> None:
        """Initialise the continual learning framework.

        Args:
            psi_threshold: PSI score threshold for drift detection.
            replay_buffer_size: Maximum experiences kept in the replay buffer.
        """
        self.knowledge_base: dict[str, KnowledgeEntry] = {}
        self.drift_history: list[DriftSignal] = []
        self.replay_buffer: list[dict[str, Any]] = []
        self._model_version: int = 0
        self._psi_threshold: float = psi_threshold
        self._replay_buffer_size: int = replay_buffer_size
        logger.info(
            "ContinualLearning initialised (psi_threshold={}, replay_buffer={})",
            psi_threshold,
            replay_buffer_size,
        )

    def detect_drift(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> DriftSignal:
        """Detect concept or data drift using Population Stability Index.

        Args:
            reference_data: Baseline distribution (n_samples × n_features or
                1-D array for a single feature).
            current_data: Current distribution with the same shape.
            feature_names: Optional names for each feature column.

        Returns:
            A :class:`DriftSignal` describing the detection result.

        Raises:
            ValueError: If ``reference_data`` and ``current_data`` have
                incompatible shapes.
        """
        reference_data = np.atleast_2d(reference_data)
        current_data = np.atleast_2d(current_data)

        if reference_data.ndim == 1:
            reference_data = reference_data.reshape(-1, 1)
        if current_data.ndim == 1:
            current_data = current_data.reshape(-1, 1)

        n_features = reference_data.shape[1]
        if current_data.shape[1] != n_features:
            raise ValueError(
                f"Shape mismatch: reference has {n_features} features, "
                f"current has {current_data.shape[1]}"
            )

        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]

        psi_scores: list[tuple[str, float]] = []
        for i, name in enumerate(feature_names):
            psi = self._compute_psi(reference_data[:, i], current_data[:, i])
            psi_scores.append((name, psi))

        max_psi = max(score for _, score in psi_scores)
        affected = [name for name, score in psi_scores if score > self._psi_threshold]
        detected = len(affected) > 0

        signal = DriftSignal(
            detected=detected,
            drift_score=round(max_psi, 4),
            affected_features=affected,
            method="psi",
        )
        self.drift_history.append(signal)

        if detected:
            logger.warning(
                "Drift detected (PSI={:.4f}) in features: {}",
                max_psi,
                affected,
            )
        else:
            logger.debug("No drift detected (max PSI={:.4f})", max_psi)

        return signal

    def _compute_psi(self, reference: np.ndarray, current: np.ndarray, n_bins: int = 10) -> float:
        """Compute PSI between two 1-D distributions.

        Args:
            reference: Reference distribution array.
            current: Current distribution array.
            n_bins: Number of histogram bins.

        Returns:
            PSI value (0 = no shift, >0.2 = significant shift).
        """
        eps = 1e-8
        bin_edges = np.percentile(reference, np.linspace(0, 100, n_bins + 1))
        bin_edges = np.unique(bin_edges)
        if len(bin_edges) < 2:
            return 0.0

        ref_counts, _ = np.histogram(reference, bins=bin_edges)
        cur_counts, _ = np.histogram(current, bins=bin_edges)

        ref_pct = ref_counts / (ref_counts.sum() + eps)
        cur_pct = cur_counts / (cur_counts.sum() + eps)

        psi = float(np.sum((cur_pct - ref_pct) * np.log((cur_pct + eps) / (ref_pct + eps))))
        return abs(psi)

    async def retrain(
        self,
        new_data: list[dict[str, Any]],
        use_replay: bool = True,
        n_epochs: int = 2,
    ) -> dict[str, Any]:
        """Incrementally retrain the model on new data with optional replay.

        Args:
            new_data: Fresh training examples.
            use_replay: When ``True``, mix in stored replay buffer samples.
            n_epochs: Number of incremental update epochs.

        Returns:
            Dictionary with training statistics including ``"loss"``,
            ``"n_samples"``, and ``"model_version"``.

        Raises:
            ValueError: If ``new_data`` is empty.
        """
        if not new_data:
            raise ValueError("new_data must not be empty")

        combined = list(new_data)
        if use_replay and self.replay_buffer:
            replay_size = min(len(self.replay_buffer), len(new_data))
            rng = np.random.default_rng(seed=42)
            replay_indices = rng.choice(len(self.replay_buffer), size=replay_size, replace=False)
            combined.extend(self.replay_buffer[i] for i in replay_indices)

        logger.info(
            "Retraining on {} samples ({} new + {} replay), {} epochs",
            len(combined),
            len(new_data),
            len(combined) - len(new_data),
            n_epochs,
        )

        rng = np.random.default_rng(seed=self._model_version)
        loss = 1.0
        for epoch in range(n_epochs):
            await asyncio.sleep(0)
            loss = max(0.05, loss * 0.7 + float(rng.normal(0, 0.02)))
            logger.debug("Retrain epoch {}/{} — loss={:.4f}", epoch + 1, n_epochs, loss)

        # Add new samples to replay buffer (FIFO)
        self.replay_buffer.extend(new_data)
        overflow = len(self.replay_buffer) - self._replay_buffer_size
        if overflow > 0:
            self.replay_buffer = self.replay_buffer[overflow:]

        self._model_version += 1
        result = {
            "loss": round(loss, 4),
            "n_samples": len(combined),
            "model_version": self._model_version,
            "epochs": n_epochs,
        }
        logger.info("Retrain complete — version={}, loss={:.4f}", self._model_version, loss)
        return result

    def update_knowledge_base(
        self,
        key: str,
        content: Any,
        confidence: float = 1.0,
    ) -> KnowledgeEntry:
        """Upsert an entry in the model knowledge base.

        Args:
            key: Unique identifier for the knowledge entry.
            content: Knowledge payload.
            confidence: Confidence weight (0–1) for this entry.

        Returns:
            The created or updated :class:`KnowledgeEntry`.

        Raises:
            ValueError: If ``confidence`` is not in [0, 1].
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {confidence}")

        existing = self.knowledge_base.get(key)
        version = (existing.version + 1) if existing else 1

        entry = KnowledgeEntry(
            key=key,
            content=content,
            version=version,
            updated_at=datetime.now(timezone.utc),
            confidence=confidence,
        )
        self.knowledge_base[key] = entry
        logger.info("Knowledge base updated: key='{}', version={}", key, version)
        return entry

    def get_knowledge(self, key: str) -> KnowledgeEntry | None:
        """Retrieve a knowledge entry by key.

        Args:
            key: Knowledge base identifier.

        Returns:
            The :class:`KnowledgeEntry` or ``None`` if not found.
        """
        return self.knowledge_base.get(key)
