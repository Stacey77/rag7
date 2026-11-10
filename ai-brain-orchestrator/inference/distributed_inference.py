"""Distributed Inference – parallel model execution using asyncio.gather.

Runs multiple inference callables concurrently and aggregates their results
into a unified output, handling partial failures gracefully.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")

# Type alias for async inference workers.
InferenceFn = Callable[[dict[str, Any]], Coroutine[Any, Any, Any]]


@dataclass
class InferenceWorker:
    """A named async inference worker.

    Attributes:
        worker_id: Unique identifier.
        fn: Async callable accepting a feature dict and returning a result.
        timeout: Maximum seconds to wait for this worker. ``None`` = no limit.
    """

    worker_id: str
    fn: InferenceFn
    timeout: float | None = None


@dataclass
class InferenceResult:
    """Aggregated output from a distributed inference run.

    Attributes:
        results: Per-worker outputs keyed by ``worker_id``.
        errors: Workers that failed, with error messages.
        elapsed_s: Wall-clock time for the parallel run.
    """

    results: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    elapsed_s: float = 0.0


class DistributedInference:
    """Parallel inference engine built on :func:`asyncio.gather`.

    Attributes:
        _workers: Registered :class:`InferenceWorker` instances keyed by ID.
    """

    def __init__(self) -> None:
        """Initialise with no registered workers."""
        self._workers: dict[str, InferenceWorker] = {}
        log.info("DistributedInference initialised")

    def register_worker(self, worker: InferenceWorker) -> None:
        """Register an inference worker.

        Args:
            worker: :class:`InferenceWorker` to add.

        Raises:
            ValueError: If a worker with the same ``worker_id`` is already registered.
        """
        if worker.worker_id in self._workers:
            raise ValueError(f"Worker '{worker.worker_id}' already registered")
        self._workers[worker.worker_id] = worker
        log.debug("Worker registered", worker_id=worker.worker_id)

    async def run_parallel(
        self,
        features: dict[str, Any],
        worker_ids: list[str] | None = None,
    ) -> InferenceResult:
        """Execute selected workers concurrently using :func:`asyncio.gather`.

        Args:
            features: Feature dict forwarded to every worker.
            worker_ids: Explicit list of workers to run. When *None* all
                registered workers are executed.

        Returns:
            :class:`InferenceResult` aggregating all worker outputs.

        Raises:
            RuntimeError: If no workers are available to run.
        """
        targets = {
            wid: w
            for wid, w in self._workers.items()
            if worker_ids is None or wid in (worker_ids or [])
        }
        if not targets:
            raise RuntimeError("No workers available for parallel inference")

        start = time.monotonic()

        async def _run_one(worker: InferenceWorker) -> tuple[str, Any, str | None]:
            try:
                coro = worker.fn(features)
                if worker.timeout is not None:
                    result = await asyncio.wait_for(coro, timeout=worker.timeout)
                else:
                    result = await coro
                return worker.worker_id, result, None
            except asyncio.TimeoutError:
                return worker.worker_id, None, "timeout"
            except Exception as exc:  # noqa: BLE001
                return worker.worker_id, None, str(exc)

        raw = await asyncio.gather(*(_run_one(w) for w in targets.values()))

        inference_result = InferenceResult(elapsed_s=time.monotonic() - start)
        for wid, result, error in raw:
            if error is None:
                inference_result.results[wid] = result
            else:
                inference_result.errors[wid] = error
                log.warning("Worker failed", worker_id=wid, error=error)

        log.info(
            "Parallel inference complete",
            succeeded=len(inference_result.results),
            failed=len(inference_result.errors),
            elapsed_s=f"{inference_result.elapsed_s:.3f}",
        )
        return inference_result

    async def aggregate_results(
        self,
        inference_result: InferenceResult,
        strategy: str = "collect",
    ) -> Any:
        """Combine worker outputs using the specified aggregation strategy.

        Supported strategies:

        * ``"collect"`` – returns a list of all successful results.
        * ``"first"`` – returns the first successful result.
        * ``"mean"`` – returns the arithmetic mean of numeric results.

        Args:
            inference_result: The :class:`InferenceResult` to aggregate.
            strategy: Aggregation strategy name.

        Returns:
            Aggregated output whose type depends on *strategy*.

        Raises:
            ValueError: If *strategy* is not recognised.
        """
        values = list(inference_result.results.values())
        if not values:
            log.warning("No results to aggregate")
            return None

        if strategy == "collect":
            return values
        elif strategy == "first":
            return values[0]
        elif strategy == "mean":
            numeric = [v for v in values if isinstance(v, (int, float))]
            if not numeric:
                raise ValueError("No numeric results available for 'mean' aggregation")
            return sum(numeric) / len(numeric)
        else:
            raise ValueError(f"Unknown aggregation strategy '{strategy}'")
