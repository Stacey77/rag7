"""Audit logging: structured event logging for all trading activity.

Provides :class:`AuditLogger` which persists structured JSON log records for
orders, executions, risk events, and compliance decisions.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger


class AuditLogger:
    """Write structured audit records for trading events.

    Records are written to a line-delimited JSON (JSONL) file and also emitted
    via :mod:`loguru` at the ``INFO`` level for real-time monitoring.

    Attributes:
        log_dir: Directory where audit log files are stored.
        log_file: Path of the active audit log file.
        max_file_size_mb: File size at which rotation is triggered.
    """

    _VALID_EVENT_TYPES: frozenset[str] = frozenset(
        [
            "order_submitted",
            "order_filled",
            "order_cancelled",
            "order_rejected",
            "risk_alert",
            "compliance_check",
            "position_update",
            "pnl_snapshot",
            "system_event",
        ]
    )

    def __init__(
        self,
        log_dir: str = "logs/audit",
        max_file_size_mb: float = 100.0,
    ) -> None:
        """Initialise AuditLogger.

        Args:
            log_dir: Directory for audit log files (created if absent).
            max_file_size_mb: Maximum log file size before rotation.
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)
        self._session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        self.log_file = self.log_dir / f"audit_{self._session_id}.jsonl"
        self._record_count = 0

        logger.info(f"AuditLogger initialised: {self.log_file}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _should_rotate(self) -> bool:
        """Check whether the current log file needs rotation.

        Returns:
            True if the file exceeds :attr:`max_file_size_bytes`.
        """
        try:
            return self.log_file.stat().st_size >= self.max_file_size_bytes
        except FileNotFoundError:
            return False

    def _rotate(self) -> None:
        """Rotate the log file by starting a new one with a sequence suffix."""
        self._session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        self.log_file = self.log_dir / f"audit_{self._session_id}.jsonl"
        logger.info(f"Audit log rotated: {self.log_file}")

    def _write_record(self, record: dict[str, Any]) -> None:
        """Append a JSON record to the audit log file.

        Args:
            record: Serialisable dict to write.
        """
        if self._should_rotate():
            self._rotate()
        with self.log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
        self._record_count += 1

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def log_event(
        self,
        event_type: str,
        data: dict[str, Any],
        severity: str = "INFO",
    ) -> dict[str, Any]:
        """Log a trading event.

        Args:
            event_type: One of the supported event type strings.
            data: Arbitrary event payload.
            severity: ``"DEBUG"``, ``"INFO"``, ``"WARNING"``, or ``"ERROR"``.

        Returns:
            The complete audit record dict (including auto-generated fields).

        Raises:
            ValueError: If *event_type* is not in the supported set.
        """
        if event_type not in self._VALID_EVENT_TYPES:
            raise ValueError(
                f"Unknown event_type '{event_type}'. "
                f"Supported: {sorted(self._VALID_EVENT_TYPES)}"
            )

        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "severity": severity,
            "sequence": self._record_count + 1,
            **data,
        }

        self._write_record(record)
        log_fn = getattr(logger, severity.lower(), logger.info)
        log_fn(f"[AUDIT] {event_type}: {json.dumps(data, default=str)[:200]}")
        return record

    def log_order(
        self,
        order_id: str,
        symbol: str,
        side: str,
        size: float,
        price: float | None,
        status: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Log an order lifecycle event.

        Args:
            order_id: Unique order identifier.
            symbol: Instrument symbol.
            side: ``"buy"`` or ``"sell"``.
            size: Order size.
            price: Limit price (None for market orders).
            status: Order status string (e.g., ``"submitted"``).
            extra: Additional fields to include in the record.

        Returns:
            Audit record dict.
        """
        event_type = f"order_{status}" if f"order_{status}" in self._VALID_EVENT_TYPES else "order_submitted"
        return self.log_event(
            event_type,
            {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "size": size,
                "price": price,
                "status": status,
                **(extra or {}),
            },
        )

    def log_risk_alert(
        self,
        alert_type: str,
        symbol: str | None,
        metric: str,
        value: float,
        threshold: float,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Log a risk management alert.

        Args:
            alert_type: Short descriptor (e.g., ``"var_breach"``).
            symbol: Affected symbol or None for portfolio-level alerts.
            metric: Risk metric name.
            value: Current metric value.
            threshold: Breach threshold.
            extra: Additional context.

        Returns:
            Audit record dict.
        """
        return self.log_event(
            "risk_alert",
            {
                "alert_type": alert_type,
                "symbol": symbol,
                "metric": metric,
                "value": value,
                "threshold": threshold,
                **(extra or {}),
            },
            severity="WARNING",
        )

    def get_recent_records(self, n: int = 100) -> list[dict[str, Any]]:
        """Read the most recent *n* records from the active log file.

        Args:
            n: Number of records to return.

        Returns:
            List of parsed record dicts (oldest first within the slice).
        """
        try:
            lines = self.log_file.read_text(encoding="utf-8").splitlines()
            records = []
            for line in lines[-n:]:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            return records
        except FileNotFoundError:
            return []
