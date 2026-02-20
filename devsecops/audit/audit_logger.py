"""Comprehensive immutable audit logging with HMAC signatures."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from loguru import logger


@dataclass
class AuditEntry:
    """A single immutable audit log entry.

    Attributes:
        entry_id: Monotonically incrementing identifier.
        event_type: Category of event (e.g. ``"TRADE_EXECUTED"``).
        actor: Identity of the user/system that triggered the event.
        resource: Resource affected (e.g. ``"order:12345"``).
        action: Specific action performed.
        details: Supplementary event data.
        outcome: ``"SUCCESS"`` or ``"FAILURE"``.
        ip_address: Originating IP address.
        timestamp: UTC ISO-8601 timestamp string.
        sequence: Global sequence number for ordering.
        signature: HMAC-SHA256 hex digest of the entry (excluding this field).
    """

    entry_id: str
    event_type: str
    actor: str
    resource: str
    action: str
    details: dict[str, Any]
    outcome: str
    ip_address: str
    timestamp: str
    sequence: int
    signature: str = ""


class AuditLogger:
    """Comprehensive immutable audit logger with HMAC-SHA256 integrity signing.

    Each log entry is signed with HMAC-SHA256 using a key sourced from the
    ``AUDIT_HMAC_KEY`` environment variable.  If the key is not set, a
    session-ephemeral random key is used (warns on startup).

    Entries are stored in-memory and can be exported to a JSON Lines file.

    Attributes:
        _entries: Ordered log entries.
        _sequence: Monotonic sequence counter.
        _hmac_key: Signing key bytes.
    """

    _ENV_KEY = "AUDIT_HMAC_KEY"

    def __init__(self) -> None:
        """Initialise the audit logger."""
        self._entries: list[AuditEntry] = []
        self._sequence: int = 0
        raw_key = os.environ.get(self._ENV_KEY)

        if raw_key:
            self._hmac_key = raw_key.encode()
            logger.info("AuditLogger: HMAC key loaded from environment")
        else:
            self._hmac_key = os.urandom(32)
            logger.warning(
                "AuditLogger: {} not set — using ephemeral HMAC key. "
                "Signatures will not be reproducible across restarts.",
                self._ENV_KEY,
            )

    def log(
        self,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        details: dict[str, Any] | None = None,
        outcome: str = "SUCCESS",
        ip_address: str = "0.0.0.0",
    ) -> AuditEntry:
        """Record an auditable event.

        Args:
            event_type: Event category.
            actor: Identity of the triggering user/system.
            resource: Affected resource identifier.
            action: Action description.
            details: Optional supplementary data.
            outcome: ``"SUCCESS"`` or ``"FAILURE"``.
            ip_address: Originating IP.

        Returns:
            The signed and appended :class:`AuditEntry`.
        """
        self._sequence += 1
        entry_id = f"audit_{self._sequence:010d}"
        timestamp = datetime.now(timezone.utc).isoformat()

        entry = AuditEntry(
            entry_id=entry_id,
            event_type=event_type,
            actor=actor,
            resource=resource,
            action=action,
            details=details or {},
            outcome=outcome,
            ip_address=ip_address,
            timestamp=timestamp,
            sequence=self._sequence,
        )
        entry.signature = self._sign(entry)
        self._entries.append(entry)
        logger.debug("Audit: [{}] {}:{} by {} → {}", event_type, resource, action, actor, outcome)
        return entry

    def verify_entry(self, entry: AuditEntry) -> bool:
        """Verify the HMAC signature of an audit entry.

        Args:
            entry: Entry to verify.

        Returns:
            ``True`` if the signature is valid (entry has not been tampered).
        """
        expected = self._sign(entry)
        return hmac.compare_digest(expected, entry.signature)

    def verify_chain(self) -> tuple[bool, list[str]]:
        """Verify the integrity of the entire audit log.

        Returns:
            Tuple of ``(all_valid, list_of_tampered_entry_ids)``.
        """
        tampered: list[str] = []
        for entry in self._entries:
            if not self.verify_entry(entry):
                tampered.append(entry.entry_id)

        if tampered:
            logger.error("Audit log integrity violation: {} tampered entries", len(tampered))
        else:
            logger.info("Audit log integrity verified: {} entries OK", len(self._entries))

        return len(tampered) == 0, tampered

    def export_jsonl(self, file_path: str) -> int:
        """Export all audit entries to a JSON Lines file.

        Args:
            file_path: Output file path.

        Returns:
            Number of entries exported.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            for entry in self._entries:
                f.write(json.dumps(asdict(entry)) + "\n")
        logger.info("Exported {} audit entries to '{}'", len(self._entries), file_path)
        return len(self._entries)

    def query(
        self,
        event_type: str | None = None,
        actor: str | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit entries with optional filters.

        Args:
            event_type: Filter by event type.
            actor: Filter by actor.
            limit: Maximum number of results to return.

        Returns:
            Matching entries (most recent first), up to ``limit``.
        """
        results = [
            e for e in reversed(self._entries)
            if (event_type is None or e.event_type == event_type)
            and (actor is None or e.actor == actor)
        ]
        return results[:limit]

    def _sign(self, entry: AuditEntry) -> str:
        """Compute the HMAC-SHA256 signature for an entry.

        The signature covers all fields except ``signature`` itself.

        Args:
            entry: Entry to sign.

        Returns:
            Hex-encoded HMAC-SHA256 digest.
        """
        payload = json.dumps(
            {
                k: v for k, v in asdict(entry).items() if k != "signature"
            },
            sort_keys=True,
            default=str,
        ).encode()
        return hmac.new(self._hmac_key, payload, hashlib.sha256).hexdigest()

    @property
    def entry_count(self) -> int:
        """Total number of logged entries."""
        return len(self._entries)
