"""Automated incident response with severity classification and runbook execution."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class Severity(Enum):
    """Incident severity levels aligned with SRE practices."""

    SEV1 = 1  # Critical: complete service outage
    SEV2 = 2  # High: major functionality impaired
    SEV3 = 3  # Medium: degraded performance
    SEV4 = 4  # Low: minor issue, workaround available
    SEV5 = 5  # Informational


class IncidentStatus(Enum):
    """Lifecycle status of an incident."""

    OPEN = auto()
    INVESTIGATING = auto()
    MITIGATING = auto()
    RESOLVED = auto()
    POSTMORTEM = auto()


@dataclass
class Incident:
    """A detected or declared operational incident.

    Attributes:
        incident_id: Unique identifier (auto-generated).
        title: Short description.
        description: Detailed incident description.
        severity: Classified severity level.
        affected_components: List of impacted service components.
        status: Current lifecycle status.
        created_at: UTC creation timestamp.
        resolved_at: UTC resolution timestamp (set on resolution).
        runbook_steps: Ordered list of response steps to execute.
        timeline: Ordered list of timestamped event strings.
        metadata: Arbitrary additional context.
    """

    incident_id: str
    title: str
    description: str
    severity: Severity
    affected_components: list[str]
    status: IncidentStatus = IncidentStatus.OPEN
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None
    runbook_steps: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunbookExecution:
    """Result of executing a single runbook step.

    Attributes:
        step: Step description.
        success: Whether execution succeeded.
        output: Execution output or error message.
        duration_ms: Execution time in milliseconds.
    """

    step: str
    success: bool
    output: str
    duration_ms: float


class IncidentResponse:
    """Automated incident handling with severity classification and runbook execution.

    Attributes:
        incidents: All incidents keyed by incident_id.
        _runbooks: Severity-to-runbook step mapping.
    """

    _SEVERITY_RUNBOOKS: dict[Severity, list[str]] = {
        Severity.SEV1: [
            "page_on_call_engineer",
            "open_war_room",
            "activate_incident_commander",
            "notify_executive_stakeholders",
            "enable_circuit_breakers",
            "failover_to_backup_region",
            "validate_failover",
            "update_status_page",
            "conduct_postmortem",
        ],
        Severity.SEV2: [
            "notify_on_call_team",
            "diagnose_root_cause",
            "apply_remediation",
            "validate_fix",
            "update_status_page",
            "schedule_postmortem",
        ],
        Severity.SEV3: [
            "notify_team_channel",
            "investigate_degradation",
            "apply_workaround",
            "monitor_for_improvement",
        ],
        Severity.SEV4: [
            "log_ticket",
            "schedule_investigation",
        ],
        Severity.SEV5: [
            "log_for_awareness",
        ],
    }

    def __init__(self) -> None:
        """Initialise the incident response system."""
        self.incidents: dict[str, Incident] = {}
        logger.info("IncidentResponse initialised")

    def classify_severity(
        self,
        error_rate: float,
        affected_user_pct: float,
        latency_p99_ms: float,
        data_loss: bool = False,
    ) -> Severity:
        """Classify incident severity from operational metrics.

        Args:
            error_rate: Fraction of requests failing (0–1).
            affected_user_pct: Percentage of users affected (0–100).
            latency_p99_ms: 99th percentile latency in milliseconds.
            data_loss: Whether data loss has occurred.

        Returns:
            Classified :class:`Severity` level.
        """
        if data_loss or error_rate > 0.5 or affected_user_pct > 50:
            return Severity.SEV1
        if error_rate > 0.2 or affected_user_pct > 20 or latency_p99_ms > 5000:
            return Severity.SEV2
        if error_rate > 0.05 or affected_user_pct > 5 or latency_p99_ms > 2000:
            return Severity.SEV3
        if error_rate > 0.01 or latency_p99_ms > 1000:
            return Severity.SEV4
        return Severity.SEV5

    def create_incident(
        self,
        title: str,
        description: str,
        severity: Severity,
        affected_components: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> Incident:
        """Create and register a new incident.

        Args:
            title: Short incident title.
            description: Detailed description.
            severity: Classified severity.
            affected_components: List of impacted components.
            metadata: Optional additional context.

        Returns:
            The newly created :class:`Incident`.
        """
        incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        runbook = self._SEVERITY_RUNBOOKS.get(severity, ["investigate_manually"])
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components,
            runbook_steps=list(runbook),
            timeline=[f"[{datetime.now(timezone.utc).isoformat()}] Incident created"],
            metadata=metadata or {},
        )
        self.incidents[incident_id] = incident
        logger.warning(
            "Incident {} created: [{}] {} ({})",
            incident_id,
            severity.name,
            title,
            affected_components,
        )
        return incident

    async def execute_runbook(self, incident_id: str) -> list[RunbookExecution]:
        """Execute the runbook associated with an incident.

        Args:
            incident_id: Incident to execute runbook for.

        Returns:
            List of :class:`RunbookExecution` results for each step.

        Raises:
            KeyError: If ``incident_id`` is not found.
        """
        incident = self._get_incident(incident_id)
        incident.status = IncidentStatus.MITIGATING
        results: list[RunbookExecution] = []

        logger.info(
            "Executing runbook for {} ({} steps): {}",
            incident_id,
            len(incident.runbook_steps),
            incident.severity.name,
        )

        for step in incident.runbook_steps:
            result = await self._execute_step(step)
            results.append(result)
            ts = datetime.now(timezone.utc).isoformat()
            status_str = "OK" if result.success else "FAILED"
            incident.timeline.append(f"[{ts}] {step}: {status_str}")
            logger.debug("Runbook step '{}': {} ({:.1f}ms)", step, status_str, result.duration_ms)

        return results

    async def resolve(self, incident_id: str, resolution_note: str = "") -> Incident:
        """Mark an incident as resolved.

        Args:
            incident_id: Incident to resolve.
            resolution_note: Optional resolution description.

        Returns:
            Updated :class:`Incident`.

        Raises:
            KeyError: If not found.
        """
        incident = self._get_incident(incident_id)
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now(timezone.utc)
        ts = incident.resolved_at.isoformat()
        incident.timeline.append(f"[{ts}] Resolved: {resolution_note or 'no note'}")
        logger.info("Incident {} resolved", incident_id)
        return incident

    async def _execute_step(self, step: str) -> RunbookExecution:
        """Simulate execution of a runbook step.

        Args:
            step: Step description.

        Returns:
            Execution result.
        """
        import time
        start = time.monotonic()
        await asyncio.sleep(0)
        duration_ms = (time.monotonic() - start) * 1000

        rng = np.random.default_rng(seed=hash(step) % (2**32))
        success = rng.random() > 0.1  # 90% success rate
        output = f"Step '{step}' {'completed successfully' if success else 'encountered an error'}"
        return RunbookExecution(
            step=step,
            success=success,
            output=output,
            duration_ms=round(duration_ms * 1000, 2),
        )

    def _get_incident(self, incident_id: str) -> Incident:
        """Retrieve an incident by ID.

        Args:
            incident_id: Incident identifier.

        Returns:
            The :class:`Incident`.

        Raises:
            KeyError: If not found.
        """
        if incident_id not in self.incidents:
            raise KeyError(f"Incident '{incident_id}' not found")
        return self.incidents[incident_id]
