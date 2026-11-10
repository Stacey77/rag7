"""Regulatory compliance checks for GDPR, SOX, and FINRA."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from loguru import logger


class Regulation(Enum):
    """Supported regulatory frameworks."""

    GDPR = auto()
    SOX = auto()
    FINRA = auto()
    PCI_DSS = auto()
    MiFID2 = auto()


class ComplianceStatus(Enum):
    """Result of a compliance check."""

    PASS = auto()
    FAIL = auto()
    WARNING = auto()
    NOT_APPLICABLE = auto()


@dataclass
class ComplianceFinding:
    """A single compliance check result.

    Attributes:
        check_id: Unique check identifier.
        regulation: Regulatory framework.
        control: Specific control or requirement identifier.
        description: Human-readable check description.
        status: Pass/fail/warning result.
        evidence: Supporting evidence or details.
        remediation: Suggested remediation if failed.
        checked_at: UTC timestamp.
    """

    check_id: str
    regulation: Regulation
    control: str
    description: str
    status: ComplianceStatus
    evidence: dict[str, Any] = field(default_factory=dict)
    remediation: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseComplianceCheck(ABC):
    """Abstract base for a compliance check.

    Subclasses implement the actual check logic for a specific
    regulatory control.
    """

    @abstractmethod
    def run(self, context: dict[str, Any]) -> ComplianceFinding:
        """Execute the compliance check.

        Args:
            context: System context data required for the check.

        Returns:
            :class:`ComplianceFinding` with the result.
        """


class GDPRDataRetentionCheck(BaseComplianceCheck):
    """GDPR Art. 5(1)(e): Data minimisation and storage limitation."""

    def run(self, context: dict[str, Any]) -> ComplianceFinding:
        """Check that PII is not retained beyond policy limits.

        Args:
            context: Must contain ``"max_retention_days"`` and
                ``"actual_retention_days"``.

        Returns:
            :class:`ComplianceFinding`.
        """
        max_days = context.get("max_retention_days", 365)
        actual_days = context.get("actual_retention_days", 0)
        status = ComplianceStatus.PASS if actual_days <= max_days else ComplianceStatus.FAIL
        return ComplianceFinding(
            check_id="GDPR-5-1-E",
            regulation=Regulation.GDPR,
            control="Art. 5(1)(e) Storage Limitation",
            description="PII retained within policy limits",
            status=status,
            evidence={"max_days": max_days, "actual_days": actual_days},
            remediation="Purge data older than retention policy" if status == ComplianceStatus.FAIL else "",
        )


class GDPREncryptionCheck(BaseComplianceCheck):
    """GDPR Art. 32: Encryption of personal data at rest and in transit."""

    def run(self, context: dict[str, Any]) -> ComplianceFinding:
        """Check that PII is encrypted at rest and in transit.

        Args:
            context: Must contain ``"encryption_at_rest"`` and
                ``"encryption_in_transit"`` booleans.

        Returns:
            :class:`ComplianceFinding`.
        """
        at_rest = context.get("encryption_at_rest", False)
        in_transit = context.get("encryption_in_transit", False)
        passed = at_rest and in_transit
        status = ComplianceStatus.PASS if passed else ComplianceStatus.FAIL
        return ComplianceFinding(
            check_id="GDPR-32",
            regulation=Regulation.GDPR,
            control="Art. 32 Security of Processing",
            description="Personal data encrypted at rest and in transit",
            status=status,
            evidence={"encryption_at_rest": at_rest, "encryption_in_transit": in_transit},
            remediation="Enable encryption for PII at rest and in transit" if not passed else "",
        )


class SOXAuditTrailCheck(BaseComplianceCheck):
    """SOX Section 404: Audit trail completeness for financial data."""

    def run(self, context: dict[str, Any]) -> ComplianceFinding:
        """Check that financial transactions have an immutable audit trail.

        Args:
            context: Must contain ``"audit_trail_enabled"`` and
                ``"audit_trail_immutable"`` booleans.

        Returns:
            :class:`ComplianceFinding`.
        """
        enabled = context.get("audit_trail_enabled", False)
        immutable = context.get("audit_trail_immutable", False)
        passed = enabled and immutable
        status = ComplianceStatus.PASS if passed else ComplianceStatus.FAIL
        return ComplianceFinding(
            check_id="SOX-404",
            regulation=Regulation.SOX,
            control="Section 404 Internal Controls",
            description="Financial transaction audit trail is complete and immutable",
            status=status,
            evidence={"enabled": enabled, "immutable": immutable},
            remediation="Enable HMAC-signed immutable audit logging" if not passed else "",
        )


class FINRARecordKeepingCheck(BaseComplianceCheck):
    """FINRA Rule 4511: Books and records retention for 6 years."""

    def run(self, context: dict[str, Any]) -> ComplianceFinding:
        """Check that trading records are retained for the required period.

        Args:
            context: Must contain ``"record_retention_years"``.

        Returns:
            :class:`ComplianceFinding`.
        """
        required_years = 6
        actual_years = context.get("record_retention_years", 0)
        passed = actual_years >= required_years
        status = ComplianceStatus.PASS if passed else ComplianceStatus.FAIL
        return ComplianceFinding(
            check_id="FINRA-4511",
            regulation=Regulation.FINRA,
            control="Rule 4511 Books and Records",
            description=f"Trading records retained for ≥{required_years} years",
            status=status,
            evidence={"required_years": required_years, "actual_years": actual_years},
            remediation=f"Extend record retention to {required_years} years" if not passed else "",
        )


class FINRABestExecutionCheck(BaseComplianceCheck):
    """FINRA Rule 5310: Best execution obligation for client orders."""

    def run(self, context: dict[str, Any]) -> ComplianceFinding:
        """Check that best execution policies are in place and monitored.

        Args:
            context: Must contain ``"best_execution_policy_enabled"`` boolean.

        Returns:
            :class:`ComplianceFinding`.
        """
        enabled = context.get("best_execution_policy_enabled", False)
        status = ComplianceStatus.PASS if enabled else ComplianceStatus.FAIL
        return ComplianceFinding(
            check_id="FINRA-5310",
            regulation=Regulation.FINRA,
            control="Rule 5310 Best Execution",
            description="Best execution policy active and monitored",
            status=status,
            evidence={"policy_enabled": enabled},
            remediation="Implement and activate best execution monitoring" if not enabled else "",
        )


class ComplianceChecker:
    """Regulatory compliance checks for GDPR, SOX, and FINRA.

    Runs a suite of abstract compliance checks against provided system
    context and generates a findings report.

    Attributes:
        _checks: Registered compliance checks.
        findings_history: All historical findings.
    """

    def __init__(self) -> None:
        """Initialise with the built-in check suite."""
        self._checks: list[BaseComplianceCheck] = [
            GDPRDataRetentionCheck(),
            GDPREncryptionCheck(),
            SOXAuditTrailCheck(),
            FINRARecordKeepingCheck(),
            FINRABestExecutionCheck(),
        ]
        self.findings_history: list[ComplianceFinding] = []
        logger.info("ComplianceChecker initialised with {} checks", len(self._checks))

    def register_check(self, check: BaseComplianceCheck) -> None:
        """Register a custom compliance check.

        Args:
            check: Check implementation to add.
        """
        self._checks.append(check)
        logger.info("Custom compliance check registered: {}", type(check).__name__)

    def run_all(self, context: dict[str, Any]) -> list[ComplianceFinding]:
        """Execute all registered compliance checks.

        Args:
            context: System context data passed to each check.

        Returns:
            List of :class:`ComplianceFinding` results.
        """
        findings: list[ComplianceFinding] = []
        for check in self._checks:
            try:
                finding = check.run(context)
                findings.append(finding)
                log = logger.warning if finding.status == ComplianceStatus.FAIL else logger.debug
                log("Check {}: {}", finding.check_id, finding.status.name)
            except Exception as exc:
                logger.error("Check {} raised: {}", type(check).__name__, exc)

        self.findings_history.extend(findings)
        passed = sum(1 for f in findings if f.status == ComplianceStatus.PASS)
        failed = sum(1 for f in findings if f.status == ComplianceStatus.FAIL)
        logger.info("Compliance run: {}/{} passed, {} failed", passed, len(findings), failed)
        return findings

    def run_for_regulation(
        self,
        regulation: Regulation,
        context: dict[str, Any],
    ) -> list[ComplianceFinding]:
        """Run only the checks for a specific regulation.

        Args:
            regulation: Target regulatory framework.
            context: System context data.

        Returns:
            Filtered list of findings.
        """
        findings = self.run_all(context)
        return [f for f in findings if f.regulation == regulation]

    def summary(self, findings: list[ComplianceFinding]) -> dict[str, Any]:
        """Generate a compliance summary.

        Args:
            findings: List of findings to summarise.

        Returns:
            Summary dictionary with counts by status and failing checks.
        """
        by_status: dict[str, int] = {}
        for f in findings:
            key = f.status.name
            by_status[key] = by_status.get(key, 0) + 1

        return {
            "total": len(findings),
            "by_status": by_status,
            "failed_checks": [
                f.check_id for f in findings if f.status == ComplianceStatus.FAIL
            ],
            "pass_rate": round(
                by_status.get("PASS", 0) / max(len(findings), 1), 4
            ),
        }
