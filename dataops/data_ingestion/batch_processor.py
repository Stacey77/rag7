"""Batch data processing with parallel execution and checkpointing."""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass
class BatchConfig:
    batch_size: int = 1000
    max_workers: int = 4
    checkpoint_enabled: bool = True
    retry_count: int = 2
    fail_fast: bool = False


@dataclass
class BatchStats:
    job_id: str = ""
    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    batches_total: int = 0
    batches_completed: int = 0
    elapsed_seconds: float = 0.0
    records_per_second: float = 0.0
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


@dataclass
class Checkpoint:
    job_id: str = ""
    last_processed_index: int = 0
    processed_ids: List[str] = field(default_factory=list)
    saved_at: datetime = field(default_factory=datetime.utcnow)


def _chunked(iterable: Iterable[T], size: int) -> Iterable[List[T]]:
    batch: List[T] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


class CheckpointStore:
    """Simple in-memory checkpoint store."""

    def __init__(self) -> None:
        self._checkpoints: Dict[str, Checkpoint] = {}

    def save(self, checkpoint: Checkpoint) -> None:
        self._checkpoints[checkpoint.job_id] = checkpoint

    def load(self, job_id: str) -> Optional[Checkpoint]:
        return self._checkpoints.get(job_id)

    def delete(self, job_id: str) -> bool:
        return bool(self._checkpoints.pop(job_id, None))


class BatchTransformer:
    """Applies a chain of transformations to each record in a batch."""

    def __init__(self) -> None:
        self._transforms: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []

    def add_transform(self, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> "BatchTransformer":
        self._transforms.append(func)
        return self

    def apply(self, record: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(record)
        for transform in self._transforms:
            result = transform(result)
        return result

    def apply_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.apply(r) for r in batch]


class BatchProcessor:
    """
    High-throughput batch processor with configurable transforms,
    retry logic, checkpointing, and progress tracking.
    """

    def __init__(self, config: Optional[BatchConfig] = None) -> None:
        self._config = config or BatchConfig()
        self._transformer = BatchTransformer()
        self._checkpoint_store = CheckpointStore()
        self._active_jobs: Dict[str, BatchStats] = {}
        logger.info("BatchProcessor initialized (batch_size=%d)", self._config.batch_size)

    def add_transform(self, func: Callable) -> "BatchProcessor":
        self._transformer.add_transform(func)
        return self

    def process(self, records: List[Dict[str, Any]],
                 output_handler: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
                 job_id: Optional[str] = None) -> BatchStats:
        job_id = job_id or str(uuid.uuid4())
        stats = BatchStats(job_id=job_id, total_records=len(records),
                           started_at=datetime.utcnow())
        self._active_jobs[job_id] = stats
        start = time.perf_counter()

        # Resume from checkpoint if available
        checkpoint = self._checkpoint_store.load(job_id)
        start_idx = checkpoint.last_processed_index if checkpoint else 0
        records_to_process = records[start_idx:]

        batches = list(_chunked(records_to_process, self._config.batch_size))
        stats.batches_total = len(batches)

        for batch_idx, batch in enumerate(batches):
            success = False
            for attempt in range(self._config.retry_count):
                try:
                    transformed = self._transformer.apply_batch(batch)
                    if output_handler:
                        output_handler(transformed)
                    stats.processed_records += len(batch)
                    stats.batches_completed += 1
                    success = True
                    break
                except Exception as exc:
                    logger.warning("Batch %d attempt %d failed: %s", batch_idx, attempt + 1, exc)
                    if attempt == self._config.retry_count - 1:
                        stats.failed_records += len(batch)
                        stats.errors.append(f"Batch {batch_idx}: {exc}")

            # Save checkpoint after each batch
            if self._config.checkpoint_enabled:
                self._checkpoint_store.save(Checkpoint(
                    job_id=job_id,
                    last_processed_index=start_idx + (batch_idx + 1) * self._config.batch_size,
                ))

            if not success and self._config.fail_fast:
                break

        elapsed = time.perf_counter() - start
        stats.elapsed_seconds = elapsed
        stats.finished_at = datetime.utcnow()
        stats.records_per_second = stats.processed_records / max(elapsed, 0.001)

        if stats.failed_records == 0:
            self._checkpoint_store.delete(job_id)

        logger.info("Batch job %s: %d/%d records, %.1f r/s",
                    job_id[:8], stats.processed_records, stats.total_records,
                    stats.records_per_second)
        return stats

    def process_stream(self, record_iter: Iterable[Dict[str, Any]],
                        output_handler: Optional[Callable] = None) -> BatchStats:
        """Process a streaming iterable in batches."""
        stats = BatchStats(job_id=str(uuid.uuid4()), started_at=datetime.utcnow())
        start = time.perf_counter()
        for batch in _chunked(record_iter, self._config.batch_size):
            try:
                transformed = self._transformer.apply_batch(batch)
                if output_handler:
                    output_handler(transformed)
                stats.processed_records += len(batch)
                stats.batches_completed += 1
            except Exception as exc:
                stats.failed_records += len(batch)
                stats.errors.append(str(exc))
        stats.elapsed_seconds = time.perf_counter() - start
        stats.finished_at = datetime.utcnow()
        stats.records_per_second = stats.processed_records / max(stats.elapsed_seconds, 0.001)
        return stats

    def get_job_stats(self, job_id: str) -> Optional[BatchStats]:
        return self._active_jobs.get(job_id)
