"""Self-healing automation agent for trading infrastructure."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class FailureType(Enum):
    """Categories of detectable infrastructure failures."""

    PROCESS_CRASH = auto()
    MEMORY_LEAK = auto()
    DEADLOCK = auto()
    NETWORK_PARTITION = auto()
    DISK_FULL = auto()
    HIGH_CPU = auto()
    SERVICE_DEGRADATION = auto()
    UNKNOWN = auto()


class RemediationStatus(Enum):
    """Outcome of a remediation action."""

    SUCCESS = auto()
    PARTIAL = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class FailureDiagnosis:
    """Result of failure diagnosis.

    Attributes:
        failure_type: Classified failure category.
        component: Affected component name.
        confidence: Diagnosis confidence (0–1).
        root_cause: Human-readable root cause summary.
        recommended_actions: Ordered list of recommended remediation steps.
        diagnosed_at: UTC timestamp.
    """

    failure_type: FailureType
    component: str
    confidence: float
    root_cause: str
    recommended_actions: list[str]
    diagnosed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RemediationResult:
    """Outcome of an automated remediation attempt.

    Attributes:
        component: Remediated component.
        action: Description of the action taken.
        status: Outcome status.
        details: Additional diagnostic information.
        executed_at: UTC timestamp.
        duration_ms: Time taken for the action.
    """

    component: str
    action: str
    status: RemediationStatus
    details: dict[str, Any] = field(default_factory=dict)
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0


class HealingAgent:
    """Autonomous self-healing agent for trading infrastructure.

    Detects infrastructure failures, diagnoses root causes using
    heuristic pattern matching, and executes remediation runbooks.

    Attributes:
        remediation_history: Log of all executed remediation actions.
        _runbooks: Mapping of failure type to remediation steps.
        _max_retries: Maximum auto-remediation attempts per incident.
    """

    # Heuristic runbooks: failure type → ordered remediation steps
    _DEFAULT_RUNBOOKS: dict[FailureType, list[str]] = {
        FailureType.PROCESS_CRASH: [
            "check_process_status",
            "collect_crash_dump",
            "restart_process",
            "verify_restart",
        ],
        FailureType.MEMORY_LEAK: [
            "capture_heap_dump",
            "graceful_restart",
            "adjust_gc_settings",
            "monitor_memory",
        ],
        FailureType.DEADLOCK: [
            "capture_thread_dump",
            "identify_contended_locks",
            "force_restart",
            "enable_deadlock_detection",
        ],
        FailureType.NETWORK_PARTITION: [
            "test_connectivity",
            "check_dns_resolution",
            "failover_to_backup",
            "notify_network_team",
        ],
        FailureType.DISK_FULL: [
            "identify_large_files",
            "rotate_logs",
            "archive_old_data",
            "alert_operations",
        ],
        FailureType.HIGH_CPU: [
            "identify_hot_processes",
            "throttle_non_critical_tasks",
            "scale_out_if_possible",
            "profile_cpu_usage",
        ],
        FailureType.SERVICE_DEGRADATION: [
            "check_downstream_dependencies",
            "enable_circuit_breaker",
            "redirect_traffic",
            "escalate_if_unresolved",
        ],
    }

    def __init__(self, max_retries: int = 3) -> None:
        """Initialise the healing agent.

        Args:
            max_retries: Maximum remediation attempts per incident.
        """
        self.remediation_history: list[RemediationResult] = []
        self._runbooks = dict(self._DEFAULT_RUNBOOKS)
        self._max_retries = max_retries
        logger.info("HealingAgent initialised (max_retries={})", max_retries)

    async def detect_failure(
        self,
        component: str,
        metrics: dict[str, float],
    ) -> FailureType | None:
        """Detect whether a component has failed based on its metrics.

        Args:
            component: Component identifier.
            metrics: Current metric readings keyed by metric name.

        Returns:
            Detected :class:`FailureType` or ``None`` if healthy.
        """
        await asyncio.sleep(0)
        thresholds: list[tuple[str, float, FailureType]] = [
            ("cpu_percent", 95.0, FailureType.HIGH_CPU),
            ("memory_percent", 98.0, FailureType.MEMORY_LEAK),
            ("disk_percent", 99.0, FailureType.DISK_FULL),
            ("error_rate", 0.5, FailureType.SERVICE_DEGRADATION),
            ("process_uptime_s", 0.0, FailureType.PROCESS_CRASH),  # 0 = not running
        ]

        for metric_name, threshold, failure_type in thresholds:
            value = metrics.get(metric_name)
            if value is not None:
                if metric_name == "process_uptime_s" and value <= threshold:
                    logger.warning("Failure detected in '{}': {}", component, failure_type.name)
                    return failure_type
                elif metric_name != "process_uptime_s" and value >= threshold:
                    logger.warning("Failure detected in '{}': {}", component, failure_type.name)
                    return failure_type

        return None

    async def diagnose(
        self,
        component: str,
        failure_type: FailureType,
        context: dict[str, Any] | None = None,
    ) -> FailureDiagnosis:
        """Diagnose the root cause of a detected failure.

        Args:
            component: Affected component.
            failure_type: Pre-classified failure type.
            context: Additional diagnostic context (logs, stack traces, etc.).

        Returns:
            :class:`FailureDiagnosis` with root cause and recommended actions.
        """
        await asyncio.sleep(0)
        context = context or {}
        rng = np.random.default_rng(seed=hash(component + failure_type.name) % (2**32))
        confidence = round(float(rng.uniform(0.65, 0.95)), 2)

        root_cause_map: dict[FailureType, str] = {
            FailureType.PROCESS_CRASH: f"{component} process exited unexpectedly (OOM or segfault)",
            FailureType.MEMORY_LEAK: f"{component} memory consumption growing unbounded",
            FailureType.DEADLOCK: f"{component} threads waiting on circular lock dependency",
            FailureType.NETWORK_PARTITION: f"{component} cannot reach required upstream services",
            FailureType.DISK_FULL: f"{component} host disk exhausted — likely log accumulation",
            FailureType.HIGH_CPU: f"{component} CPU saturated — possible hot-loop or thundering herd",
            FailureType.SERVICE_DEGRADATION: f"{component} exhibiting elevated error rates",
            FailureType.UNKNOWN: f"{component} exhibiting anomalous behaviour",
        }

        recommended_actions = self._runbooks.get(failure_type, ["manual_investigation"])
        diagnosis = FailureDiagnosis(
            failure_type=failure_type,
            component=component,
            confidence=confidence,
            root_cause=root_cause_map.get(failure_type, "unknown"),
            recommended_actions=recommended_actions,
        )
        logger.info(
            "Diagnosis for '{}': {} (confidence={:.0%}) — {}",
            component,
            failure_type.name,
            confidence,
            diagnosis.root_cause,
        )
        return diagnosis

    async def remediate(
        self,
        diagnosis: FailureDiagnosis,
    ) -> list[RemediationResult]:
        """Execute the remediation runbook for a diagnosed failure.

        Args:
            diagnosis: Completed diagnosis from :meth:`diagnose`.

        Returns:
            List of :class:`RemediationResult` for each executed step.
        """
        results: list[RemediationResult] = []
        actions = diagnosis.recommended_actions

        logger.info(
            "Remediating '{}' ({}): {} steps",
            diagnosis.component,
            diagnosis.failure_type.name,
            len(actions),
        )

        for attempt in range(1, self._max_retries + 1):
            for action in actions:
                result = await self._execute_action(diagnosis.component, action)
                results.append(result)
                self.remediation_history.append(result)

                if result.status == RemediationStatus.FAILED:
                    logger.warning(
                        "Action '{}' failed on attempt {} — continuing", action, attempt
                    )
                else:
                    logger.info("Action '{}' → {}", action, result.status.name)

            # Check if remediation was successful
            if all(r.status in (RemediationStatus.SUCCESS, RemediationStatus.SKIPPED)
                   for r in results):
                logger.info(
                    "Remediation complete for '{}' after {} step(s)", diagnosis.component, len(results)
                )
                return results

        logger.error(
            "Remediation exhausted for '{}' after {} attempts", diagnosis.component, self._max_retries
        )
        return results

    async def _execute_action(self, component: str, action: str) -> RemediationResult:
        """Execute a single remediation action (simulated).

        Args:
            component: Target component.
            action: Action name from the runbook.

        Returns:
            :class:`RemediationResult` for the executed action.
        """
        import time
        start = time.monotonic()
        await asyncio.sleep(0)
        duration_ms = (time.monotonic() - start) * 1000

        rng = np.random.default_rng(seed=hash(component + action) % (2**32))
        success_prob = 0.85
        status = (
            RemediationStatus.SUCCESS
            if rng.random() < success_prob
            else RemediationStatus.PARTIAL
        )

        return RemediationResult(
            component=component,
            action=action,
            status=status,
            details={"simulated": True},
            duration_ms=round(duration_ms * 100, 2),
        )
