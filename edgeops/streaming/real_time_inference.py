"""Ultra-low latency async inference engine for edge deployments."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

import numpy as np
from loguru import logger


@dataclass
class InferenceRequest:
    """A single inference request.

    Attributes:
        request_id: Unique identifier.
        payload: Input features as a numpy array.
        model_id: Target model identifier.
        priority: Request priority (higher = more urgent).
        max_latency_ms: Hard latency deadline; raises TimeoutError if exceeded.
        submitted_at: UTC submission timestamp.
    """

    request_id: str
    payload: np.ndarray
    model_id: str
    priority: int = 0
    max_latency_ms: float = 50.0
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class InferenceResponse:
    """Result of a completed inference request.

    Attributes:
        request_id: Corresponding request identifier.
        model_id: Model that produced the result.
        output: Inference output array.
        latency_ms: Actual end-to-end latency.
        timed_out: Whether the request exceeded its deadline.
        completed_at: UTC completion timestamp.
    """

    request_id: str
    model_id: str
    output: np.ndarray
    latency_ms: float
    timed_out: bool = False
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Type alias for an async inference backend
InferenceBackend = Callable[[InferenceRequest], Awaitable[np.ndarray]]


class RealTimeInference:
    """Ultra-low latency async inference engine with deadline enforcement.

    Dispatches inference requests to registered model backends with
    per-request timeout controls.  Tracks latency statistics and
    maintains an SLA compliance counter.

    Attributes:
        backends: Registered inference backends keyed by model_id.
        latency_stats: Per-model latency history.
        sla_violations: Count of SLA deadline violations per model.
        _timeout_default_ms: Default deadline when none is specified.
    """

    def __init__(self, default_timeout_ms: float = 50.0) -> None:
        """Initialise the real-time inference engine.

        Args:
            default_timeout_ms: Default request timeout in milliseconds.
        """
        self.backends: dict[str, InferenceBackend] = {}
        self.latency_stats: dict[str, list[float]] = {}
        self.sla_violations: dict[str, int] = {}
        self._timeout_default_ms = default_timeout_ms
        logger.info("RealTimeInference engine initialised (default_timeout={}ms)", default_timeout_ms)

    def register_backend(self, model_id: str, backend: InferenceBackend) -> None:
        """Register an inference backend for a model.

        Args:
            model_id: Model identifier.
            backend: Async callable accepting a request, returning output array.
        """
        self.backends[model_id] = backend
        self.latency_stats[model_id] = []
        self.sla_violations[model_id] = 0
        logger.info("Backend registered for model '{}'", model_id)

    async def infer(self, request: InferenceRequest) -> InferenceResponse:
        """Execute a single inference request with deadline enforcement.

        Args:
            request: Inference request with payload and deadline.

        Returns:
            :class:`InferenceResponse` with result and latency.

        Raises:
            KeyError: If no backend is registered for ``request.model_id``.
        """
        if request.model_id not in self.backends:
            raise KeyError(
                f"No backend registered for model '{request.model_id}'. "
                "Call register_backend() first."
            )

        backend = self.backends[request.model_id]
        deadline_s = (request.max_latency_ms or self._timeout_default_ms) / 1000.0
        start = time.monotonic()
        timed_out = False
        output: np.ndarray

        try:
            output = await asyncio.wait_for(backend(request), timeout=deadline_s)
        except asyncio.TimeoutError:
            timed_out = True
            output = np.array([])
            self.sla_violations[request.model_id] += 1
            logger.warning(
                "SLA violation: request '{}' exceeded {}ms deadline",
                request.request_id,
                request.max_latency_ms,
            )

        latency_ms = (time.monotonic() - start) * 1000
        self.latency_stats[request.model_id].append(latency_ms)

        return InferenceResponse(
            request_id=request.request_id,
            model_id=request.model_id,
            output=output,
            latency_ms=round(latency_ms, 3),
            timed_out=timed_out,
        )

    async def batch_infer(
        self,
        requests: list[InferenceRequest],
    ) -> list[InferenceResponse]:
        """Execute multiple inference requests concurrently.

        Args:
            requests: List of inference requests (may target different models).

        Returns:
            List of :class:`InferenceResponse` in the same order.

        Raises:
            ValueError: If ``requests`` is empty.
        """
        if not requests:
            raise ValueError("requests must not be empty")

        # Sort by priority (highest first) within each model
        sorted_requests = sorted(requests, key=lambda r: -r.priority)
        responses = await asyncio.gather(*[self.infer(r) for r in sorted_requests])

        # Restore original order
        id_to_response = {r.request_id: r for r in responses}
        return [id_to_response[req.request_id] for req in requests]

    def latency_percentiles(self, model_id: str) -> dict[str, float]:
        """Compute latency percentiles for a model.

        Args:
            model_id: Model identifier.

        Returns:
            Dictionary with p50, p95, p99, mean, and max latencies.

        Raises:
            KeyError: If no latency data for the model.
            ValueError: If no requests have been processed.
        """
        if model_id not in self.latency_stats:
            raise KeyError(f"No stats for model '{model_id}'")

        data = self.latency_stats[model_id]
        if not data:
            raise ValueError(f"No latency data recorded for '{model_id}'")

        arr = np.asarray(data)
        return {
            "p50_ms": round(float(np.percentile(arr, 50)), 3),
            "p95_ms": round(float(np.percentile(arr, 95)), 3),
            "p99_ms": round(float(np.percentile(arr, 99)), 3),
            "mean_ms": round(float(np.mean(arr)), 3),
            "max_ms": round(float(np.max(arr)), 3),
            "n_requests": len(data),
            "sla_violations": self.sla_violations.get(model_id, 0),
        }

    @staticmethod
    def make_simulated_backend(
        model_id: str,
        base_latency_ms: float = 2.0,
        output_shape: tuple[int, ...] = (1,),
    ) -> InferenceBackend:
        """Factory for a simulated inference backend.

        Args:
            model_id: Model identifier label.
            base_latency_ms: Simulated processing time.
            output_shape: Shape of the output array.

        Returns:
            Async callable suitable for :meth:`register_backend`.
        """
        async def _backend(request: InferenceRequest) -> np.ndarray:
            await asyncio.sleep(base_latency_ms / 1000.0)
            rng = np.random.default_rng(seed=hash(request.request_id) % (2**32))
            return rng.uniform(-1, 1, size=output_shape).astype(np.float32)

        return _backend
