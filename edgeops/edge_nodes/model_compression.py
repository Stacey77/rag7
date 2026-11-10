"""Model quantisation and pruning simulation for edge deployment."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class CompressionMethod(Enum):
    """Available model compression techniques."""

    INT8_QUANTIZATION = auto()
    INT4_QUANTIZATION = auto()
    FP16_QUANTIZATION = auto()
    MAGNITUDE_PRUNING = auto()
    STRUCTURED_PRUNING = auto()
    KNOWLEDGE_DISTILLATION = auto()


@dataclass
class ModelSpec:
    """Specification of a model to be compressed.

    Attributes:
        model_id: Unique model identifier.
        parameter_count: Total number of float32 parameters.
        size_mb: Model size in megabytes.
        baseline_accuracy: Accuracy before compression.
        target_latency_ms: Target inference latency on edge device.
    """

    model_id: str
    parameter_count: int
    size_mb: float
    baseline_accuracy: float
    target_latency_ms: float = 10.0


@dataclass
class CompressionResult:
    """Result of a model compression operation.

    Attributes:
        model_id: Identifier of the compressed model.
        method: Compression technique applied.
        original_size_mb: Size before compression.
        compressed_size_mb: Size after compression.
        compression_ratio: original / compressed.
        accuracy_after: Model accuracy after compression.
        accuracy_delta: Accuracy change (negative = degradation).
        estimated_latency_ms: Estimated inference latency after compression.
        meets_latency_target: Whether the latency target is met.
        compressed_at: UTC timestamp.
    """

    model_id: str
    method: CompressionMethod
    original_size_mb: float
    compressed_size_mb: float
    compression_ratio: float
    accuracy_after: float
    accuracy_delta: float
    estimated_latency_ms: float
    meets_latency_target: bool
    compressed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Compression method characteristics (ratio_range, accuracy_penalty_range)
_METHOD_PROFILES: dict[CompressionMethod, tuple[tuple[float, float], tuple[float, float]]] = {
    CompressionMethod.INT8_QUANTIZATION: ((3.5, 4.5), (0.001, 0.01)),
    CompressionMethod.INT4_QUANTIZATION: ((7.0, 9.0), (0.01, 0.05)),
    CompressionMethod.FP16_QUANTIZATION: ((1.8, 2.2), (0.0001, 0.002)),
    CompressionMethod.MAGNITUDE_PRUNING: ((2.0, 5.0), (0.005, 0.03)),
    CompressionMethod.STRUCTURED_PRUNING: ((3.0, 8.0), (0.01, 0.06)),
    CompressionMethod.KNOWLEDGE_DISTILLATION: ((4.0, 10.0), (0.005, 0.02)),
}


class ModelCompression:
    """Model quantisation and pruning simulation for edge deployment.

    Simulates compression operations tracking compression ratio and
    accuracy trade-off without requiring actual model weights.

    Attributes:
        compression_history: Log of all compression results.
    """

    def __init__(self) -> None:
        """Initialise the model compression manager."""
        self.compression_history: list[CompressionResult] = []
        logger.info("ModelCompression initialised")

    def quantize(
        self,
        model_spec: ModelSpec,
        method: CompressionMethod = CompressionMethod.INT8_QUANTIZATION,
        random_seed: int = 42,
    ) -> CompressionResult:
        """Simulate model quantisation.

        Args:
            model_spec: Specification of the model to compress.
            method: Quantisation method to apply.
            random_seed: Seed for reproducible simulation.

        Returns:
            :class:`CompressionResult` with simulated metrics.

        Raises:
            ValueError: If ``method`` is not a quantisation method.
        """
        quantisation_methods = {
            CompressionMethod.INT8_QUANTIZATION,
            CompressionMethod.INT4_QUANTIZATION,
            CompressionMethod.FP16_QUANTIZATION,
        }
        if method not in quantisation_methods:
            raise ValueError(
                f"Method {method.name} is not a quantisation method. "
                f"Use one of: {[m.name for m in quantisation_methods]}"
            )
        return self._compress(model_spec, method, random_seed)

    def prune(
        self,
        model_spec: ModelSpec,
        sparsity: float = 0.5,
        structured: bool = False,
        random_seed: int = 42,
    ) -> CompressionResult:
        """Simulate model pruning.

        Args:
            model_spec: Model specification.
            sparsity: Fraction of weights to zero out (0–1).
            structured: Use structured (channel) pruning if True, else
                magnitude-based unstructured pruning.
            random_seed: Seed for reproducible simulation.

        Returns:
            :class:`CompressionResult`.

        Raises:
            ValueError: If ``sparsity`` is not in (0, 1).
        """
        if not 0 < sparsity < 1:
            raise ValueError(f"sparsity must be in (0, 1), got {sparsity}")

        method = (
            CompressionMethod.STRUCTURED_PRUNING
            if structured
            else CompressionMethod.MAGNITUDE_PRUNING
        )
        result = self._compress(model_spec, method, random_seed)
        # Scale accuracy penalty with sparsity
        extra_penalty = sparsity * 0.05
        result.accuracy_after = round(
            max(0.0, result.accuracy_after - extra_penalty), 4
        )
        result.accuracy_delta = round(
            result.accuracy_after - model_spec.baseline_accuracy, 4
        )
        return result

    def compress_pipeline(
        self,
        model_spec: ModelSpec,
        methods: list[CompressionMethod],
    ) -> list[CompressionResult]:
        """Apply a sequence of compression techniques.

        Each method is applied to the output of the previous step.

        Args:
            model_spec: Original model specification.
            methods: Ordered list of compression methods.

        Returns:
            List of :class:`CompressionResult` for each step.
        """
        results: list[CompressionResult] = []
        current_spec = model_spec

        for i, method in enumerate(methods):
            result = self._compress(current_spec, method, random_seed=i)
            results.append(result)
            # Update spec for next step
            current_spec = ModelSpec(
                model_id=current_spec.model_id,
                parameter_count=int(current_spec.parameter_count / result.compression_ratio),
                size_mb=result.compressed_size_mb,
                baseline_accuracy=result.accuracy_after,
                target_latency_ms=current_spec.target_latency_ms,
            )

        logger.info(
            "Compression pipeline for '{}': {} steps, final ratio={:.2f}×",
            model_spec.model_id,
            len(methods),
            model_spec.size_mb / results[-1].compressed_size_mb if results else 1.0,
        )
        return results

    def _compress(
        self,
        model_spec: ModelSpec,
        method: CompressionMethod,
        random_seed: int,
    ) -> CompressionResult:
        """Core compression simulation.

        Args:
            model_spec: Model to compress.
            method: Compression method.
            random_seed: RNG seed.

        Returns:
            Simulated :class:`CompressionResult`.
        """
        ratio_range, penalty_range = _METHOD_PROFILES[method]
        rng = np.random.default_rng(seed=random_seed)

        ratio = float(rng.uniform(*ratio_range))
        accuracy_penalty = float(rng.uniform(*penalty_range))
        compressed_size = model_spec.size_mb / ratio
        accuracy_after = max(0.0, model_spec.baseline_accuracy - accuracy_penalty)
        estimated_latency = model_spec.target_latency_ms / ratio * 0.8  # heuristic

        result = CompressionResult(
            model_id=model_spec.model_id,
            method=method,
            original_size_mb=round(model_spec.size_mb, 2),
            compressed_size_mb=round(compressed_size, 2),
            compression_ratio=round(ratio, 2),
            accuracy_after=round(accuracy_after, 4),
            accuracy_delta=round(accuracy_after - model_spec.baseline_accuracy, 4),
            estimated_latency_ms=round(estimated_latency, 2),
            meets_latency_target=estimated_latency <= model_spec.target_latency_ms,
        )
        self.compression_history.append(result)
        logger.info(
            "Compressed '{}' with {}: ratio={:.2f}×, accuracy_delta={:+.4f}",
            model_spec.model_id,
            method.name,
            ratio,
            result.accuracy_delta,
        )
        return result
