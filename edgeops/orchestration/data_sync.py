"""Edge-to-cloud data synchronisation with conflict resolution."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from loguru import logger


class ConflictStrategy(Enum):
    """Conflict resolution strategies for concurrent updates."""

    LAST_WRITE_WINS = auto()    # Most recent timestamp wins
    SERVER_WINS = auto()        # Cloud/server version always wins
    CLIENT_WINS = auto()        # Edge/client version always wins
    MERGE = auto()              # Attempt automatic field-level merge


@dataclass
class DataRecord:
    """A versioned data record subject to synchronisation.

    Attributes:
        record_id: Unique identifier.
        data: Record payload.
        version: Monotonically increasing version counter.
        updated_at: UTC timestamp of last update.
        checksum: SHA-256 checksum of serialised data.
        source: ``"edge"`` or ``"cloud"``.
    """

    record_id: str
    data: Any
    version: int
    updated_at: datetime
    checksum: str
    source: str = "edge"

    @classmethod
    def create(cls, record_id: str, data: Any, source: str = "edge") -> "DataRecord":
        """Create a new DataRecord with computed checksum.

        Args:
            record_id: Record identifier.
            data: Record payload.
            source: Originating source.

        Returns:
            New :class:`DataRecord`.
        """
        checksum = hashlib.sha256(str(data).encode()).hexdigest()[:16]
        return cls(
            record_id=record_id,
            data=data,
            version=1,
            updated_at=datetime.now(timezone.utc),
            checksum=checksum,
            source=source,
        )


@dataclass
class SyncResult:
    """Result of a synchronisation operation.

    Attributes:
        synced_records: IDs of successfully synced records.
        conflicts_resolved: IDs of records where conflicts were resolved.
        failed_records: IDs of records that failed to sync.
        bytes_transferred: Estimated bytes transferred.
        duration_ms: Sync operation duration.
        sync_at: UTC timestamp.
    """

    synced_records: list[str]
    conflicts_resolved: list[str]
    failed_records: list[str]
    bytes_transferred: int
    duration_ms: float
    sync_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success_rate(self) -> float:
        """Fraction of records synced successfully."""
        total = len(self.synced_records) + len(self.failed_records)
        return len(self.synced_records) / total if total > 0 else 1.0


class DataSync:
    """Edge-to-cloud data synchronisation with conflict resolution.

    Maintains local and remote record stores, tracks sync state,
    and implements configurable conflict resolution strategies.

    Attributes:
        local_store: Edge-side data records keyed by record_id.
        remote_store: Cloud-side data records keyed by record_id.
        conflict_log: History of resolved conflicts.
        sync_history: History of sync operations.
        _strategy: Conflict resolution strategy.
    """

    def __init__(self, strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS) -> None:
        """Initialise the data sync manager.

        Args:
            strategy: Conflict resolution strategy.
        """
        self.local_store: dict[str, DataRecord] = {}
        self.remote_store: dict[str, DataRecord] = {}
        self.conflict_log: list[dict[str, Any]] = []
        self.sync_history: list[SyncResult] = []
        self._strategy = strategy
        logger.info("DataSync initialised (strategy={})", strategy.name)

    def upsert_local(self, record_id: str, data: Any) -> DataRecord:
        """Create or update a record in the local (edge) store.

        Args:
            record_id: Record identifier.
            data: Record payload.

        Returns:
            Created or updated :class:`DataRecord`.
        """
        existing = self.local_store.get(record_id)
        if existing:
            checksum = hashlib.sha256(str(data).encode()).hexdigest()[:16]
            record = DataRecord(
                record_id=record_id,
                data=data,
                version=existing.version + 1,
                updated_at=datetime.now(timezone.utc),
                checksum=checksum,
                source="edge",
            )
        else:
            record = DataRecord.create(record_id, data, source="edge")
        self.local_store[record_id] = record
        return record

    async def sync(
        self,
        record_ids: list[str] | None = None,
    ) -> SyncResult:
        """Synchronise local records to the remote store.

        Performs an incremental sync of records that differ from the
        remote version.  Conflicts are resolved using ``self._strategy``.

        Args:
            record_ids: Subset of records to sync; syncs all if ``None``.

        Returns:
            :class:`SyncResult` summarising the operation.
        """
        import time
        start = time.monotonic()

        targets = record_ids or list(self.local_store.keys())
        synced: list[str] = []
        conflicts: list[str] = []
        failed: list[str] = []
        bytes_tx = 0

        for record_id in targets:
            try:
                local = self.local_store.get(record_id)
                if local is None:
                    logger.debug("Record '{}' not in local store, skipping", record_id)
                    continue

                remote = self.remote_store.get(record_id)
                resolved = self._resolve(local, remote)

                if resolved is None:
                    # No change needed
                    synced.append(record_id)
                    continue

                if remote and resolved.checksum != local.checksum and resolved.checksum != (remote.checksum if remote else ""):
                    conflicts.append(record_id)

                await asyncio.sleep(0)
                self.remote_store[record_id] = resolved
                bytes_tx += len(str(resolved.data).encode())
                synced.append(record_id)

            except Exception as exc:
                logger.error("Sync failed for record '{}': {}", record_id, exc)
                failed.append(record_id)

        duration_ms = (time.monotonic() - start) * 1000
        result = SyncResult(
            synced_records=synced,
            conflicts_resolved=conflicts,
            failed_records=failed,
            bytes_transferred=bytes_tx,
            duration_ms=round(duration_ms, 2),
        )
        self.sync_history.append(result)
        logger.info(
            "Sync complete: {}/{} records, {} conflicts, {} failed, {} bytes",
            len(synced),
            len(targets),
            len(conflicts),
            len(failed),
            bytes_tx,
        )
        return result

    async def pull(self, record_ids: list[str] | None = None) -> int:
        """Pull updates from the remote store to local.

        Args:
            record_ids: Records to pull; all remote records if ``None``.

        Returns:
            Number of records updated locally.
        """
        await asyncio.sleep(0)
        targets = record_ids or list(self.remote_store.keys())
        updated = 0

        for record_id in targets:
            remote = self.remote_store.get(record_id)
            if remote is None:
                continue
            local = self.local_store.get(record_id)
            if local is None or remote.version > local.version:
                self.local_store[record_id] = remote
                updated += 1

        logger.debug("Pull complete: {} records updated", updated)
        return updated

    def _resolve(
        self,
        local: DataRecord,
        remote: DataRecord | None,
    ) -> DataRecord | None:
        """Resolve a potential conflict between local and remote records.

        Args:
            local: Local record.
            remote: Remote record (may be ``None`` if first sync).

        Returns:
            The record to write to remote, or ``None`` if no update needed.
        """
        if remote is None:
            return local  # New record — always push

        if local.checksum == remote.checksum:
            return None  # Identical — no sync needed

        # Conflict detected
        self.conflict_log.append({
            "record_id": local.record_id,
            "local_version": local.version,
            "remote_version": remote.version,
            "strategy": self._strategy.name,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        })

        if self._strategy == ConflictStrategy.LAST_WRITE_WINS:
            return local if local.updated_at >= remote.updated_at else remote
        elif self._strategy == ConflictStrategy.SERVER_WINS:
            return remote
        elif self._strategy == ConflictStrategy.CLIENT_WINS:
            return local
        elif self._strategy == ConflictStrategy.MERGE:
            return self._merge(local, remote)

        return local  # Default fallback

    def _merge(self, local: DataRecord, remote: DataRecord) -> DataRecord:
        """Attempt a simple field-level merge of two records.

        Merges dict payloads by taking the most-recently-updated value
        for each conflicting key.

        Args:
            local: Local record.
            remote: Remote record.

        Returns:
            Merged :class:`DataRecord`.
        """
        if isinstance(local.data, dict) and isinstance(remote.data, dict):
            merged_data = {**remote.data}
            if local.updated_at >= remote.updated_at:
                merged_data.update(local.data)
        else:
            # Non-dict: fall back to last-write-wins
            merged_data = local.data if local.updated_at >= remote.updated_at else remote.data

        return DataRecord.create(
            local.record_id,
            merged_data,
            source="merged",
        )
