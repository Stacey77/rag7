"""Security deployment gates: checkpoints before production deployment."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Awaitable

from loguru import logger


class GateStatus(Enum):
    """Status of a deployment gate evaluation."""

    OPEN = auto()    # Gate passed
    BLOCKED = auto() # Gate failed
    SKIPPED = auto() # Gate not applicable
    ERROR = auto()   # Gate evaluation error


@dataclass
class GateResult:
    """Result of a single deployment gate evaluation.

    Attributes:
        gate_name: Name of the gate.
        status: Evaluation outcome.
        message: Human-readable result description.
        details: Supplementary data.
        evaluated_at: UTC timestamp.
    """

    gate_name: str
    status: GateStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DeploymentDecision:
    """Final deployment go/no-go decision.

    Attributes:
        deployment_id: Identifier of the deployment being evaluated.
        approved: Whether deployment is approved.
        gate_results: Results for all evaluated gates.
        blocking_gates: Names of gates that blocked deployment.
        evaluated_at: UTC timestamp.
    """

    deployment_id: str
    approved: bool
    gate_results: list[GateResult]
    blocking_gates: list[str]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DeploymentGates:
    """Security checkpoints evaluated before production deployment.

    Gates are composed async functions that inspect a deployment context
    and return pass/fail decisions.  All required gates must pass for
    a deployment to be approved.

    Attributes:
        gates: Registered gate functions.
        evaluation_history: All past deployment decisions.
    """

    def __init__(self) -> None:
        """Initialise the deployment gates with built-in checks."""
        self.gates: dict[str, Callable[[dict[str, Any]], Awaitable[GateResult]]] = {}
        self.evaluation_history: list[DeploymentDecision] = []
        self._register_default_gates()
        logger.info("DeploymentGates initialised ({} default gates)", len(self.gates))

    def register_gate(
        self,
        name: str,
        gate_fn: Callable[[dict[str, Any]], Awaitable[GateResult]],
    ) -> None:
        """Register a custom deployment gate.

        Args:
            name: Unique gate name.
            gate_fn: Async callable ``(context) → GateResult``.
        """
        self.gates[name] = gate_fn
        logger.debug("Deployment gate '{}' registered", name)

    async def evaluate(
        self,
        deployment_id: str,
        context: dict[str, Any],
        gate_names: list[str] | None = None,
    ) -> DeploymentDecision:
        """Evaluate all (or specified) gates for a deployment.

        Args:
            deployment_id: Deployment identifier.
            context: Deployment context (build results, scan results, etc.).
            gate_names: Subset of gate names to evaluate; all if None.

        Returns:
            :class:`DeploymentDecision` with go/no-go verdict.
        """
        targets = gate_names or list(self.gates.keys())
        results: list[GateResult] = []

        for gate_name in targets:
            gate_fn = self.gates.get(gate_name)
            if gate_fn is None:
                results.append(GateResult(
                    gate_name=gate_name,
                    status=GateStatus.ERROR,
                    message=f"Gate '{gate_name}' not registered",
                ))
                continue
            try:
                result = await gate_fn(context)
            except Exception as exc:
                logger.error("Gate '{}' evaluation error: {}", gate_name, exc)
                result = GateResult(
                    gate_name=gate_name,
                    status=GateStatus.ERROR,
                    message=str(exc),
                )
            results.append(result)

        blocking = [
            r.gate_name for r in results
            if r.status in (GateStatus.BLOCKED, GateStatus.ERROR)
        ]
        approved = len(blocking) == 0

        decision = DeploymentDecision(
            deployment_id=deployment_id,
            approved=approved,
            gate_results=results,
            blocking_gates=blocking,
        )
        self.evaluation_history.append(decision)
        log = logger.info if approved else logger.error
        log(
            "Deployment '{}': {} ({} gates, {} blocking)",
            deployment_id,
            "APPROVED" if approved else "BLOCKED",
            len(results),
            len(blocking),
        )
        return decision

    def _register_default_gates(self) -> None:
        """Register built-in security gates."""

        async def no_critical_vulns(ctx: dict[str, Any]) -> GateResult:
            critical = ctx.get("critical_vulnerabilities", 0)
            passed = critical == 0
            return GateResult(
                gate_name="no_critical_vulnerabilities",
                status=GateStatus.OPEN if passed else GateStatus.BLOCKED,
                message=f"Critical vulnerabilities: {critical}",
                details={"critical_count": critical},
            )

        async def sast_passed(ctx: dict[str, Any]) -> GateResult:
            passed = ctx.get("sast_passed", True)
            return GateResult(
                gate_name="sast_passed",
                status=GateStatus.OPEN if passed else GateStatus.BLOCKED,
                message="SAST scan passed" if passed else "SAST scan failed",
            )

        async def tests_passed(ctx: dict[str, Any]) -> GateResult:
            coverage = ctx.get("test_coverage_pct", 100.0)
            min_coverage = ctx.get("min_coverage_pct", 80.0)
            passed = coverage >= min_coverage
            return GateResult(
                gate_name="test_coverage",
                status=GateStatus.OPEN if passed else GateStatus.BLOCKED,
                message=f"Coverage {coverage:.1f}% {'≥' if passed else '<'} {min_coverage:.1f}%",
                details={"coverage_pct": coverage, "min_pct": min_coverage},
            )

        async def secrets_not_leaked(ctx: dict[str, Any]) -> GateResult:
            secrets_found = ctx.get("secrets_detected", 0)
            passed = secrets_found == 0
            return GateResult(
                gate_name="no_secrets_leaked",
                status=GateStatus.OPEN if passed else GateStatus.BLOCKED,
                message=f"Secrets detected: {secrets_found}",
                details={"secrets_count": secrets_found},
            )

        for name, fn in [
            ("no_critical_vulnerabilities", no_critical_vulns),
            ("sast_passed", sast_passed),
            ("test_coverage", tests_passed),
            ("no_secrets_leaked", secrets_not_leaked),
        ]:
            self.gates[name] = fn
