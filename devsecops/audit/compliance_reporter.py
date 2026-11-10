"""Regulatory compliance reporting for trading platform audits."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, date, timezone
from typing import Any

from loguru import logger


@dataclass
class ReportPeriod:
    """Date range for a compliance report.

    Attributes:
        start: Inclusive start date.
        end: Inclusive end date.
    """

    start: date
    end: date

    def __post_init__(self) -> None:
        """Validate that start ≤ end."""
        if self.start > self.end:
            raise ValueError(f"start {self.start} must not be after end {self.end}")

    @property
    def days(self) -> int:
        """Number of days in the period."""
        return (self.end - self.start).days + 1


@dataclass
class ComplianceReport:
    """A generated regulatory compliance report.

    Attributes:
        report_id: Unique identifier.
        regulation: Target regulation (e.g. ``"FINRA"``, ``"MiFID2"``).
        period: Reporting period.
        entity_id: Regulated entity identifier.
        sections: Named report sections with their content.
        findings: List of compliance findings/issues.
        attestation: Attestation statement.
        generated_at: UTC generation timestamp.
        status: ``"DRAFT"`` or ``"FINAL"``.
    """

    report_id: str
    regulation: str
    period: ReportPeriod
    entity_id: str
    sections: dict[str, Any]
    findings: list[dict[str, Any]]
    attestation: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "DRAFT"


class ComplianceReporter:
    """Regulatory report generation for trading compliance obligations.

    Generates structured compliance reports for FINRA, MiFID2, and
    other regulatory frameworks based on audit log and trade data.

    Attributes:
        generated_reports: All generated reports keyed by report_id.
        _report_counter: Report ID counter.
    """

    _SUPPORTED_REGULATIONS: set[str] = {"FINRA", "MiFID2", "SOX", "GDPR", "SEC"}

    def __init__(self) -> None:
        """Initialise the compliance reporter."""
        self.generated_reports: dict[str, ComplianceReport] = {}
        self._report_counter = 0
        logger.info("ComplianceReporter initialised")

    def generate_finra_report(
        self,
        entity_id: str,
        period: ReportPeriod,
        trade_data: list[dict[str, Any]],
        audit_events: list[dict[str, Any]],
    ) -> ComplianceReport:
        """Generate a FINRA compliance report.

        Args:
            entity_id: Regulated entity identifier.
            period: Reporting period.
            trade_data: Trade execution records for the period.
            audit_events: Audit log entries for the period.

        Returns:
            Generated :class:`ComplianceReport`.
        """
        report_id = self._next_report_id("FINRA")
        total_trades = len(trade_data)
        total_value = sum(
            t.get("quantity", 0) * t.get("price", 0) for t in trade_data
        )

        sections = {
            "executive_summary": {
                "entity": entity_id,
                "period": f"{period.start} to {period.end}",
                "total_trades": total_trades,
                "total_notional_value": round(total_value, 2),
                "reporting_obligation": "FINRA Rule 4511 Books and Records",
            },
            "trade_activity": self._summarise_trades(trade_data),
            "best_execution": self._best_execution_analysis(trade_data),
            "supervisory_controls": {
                "audit_events_reviewed": len(audit_events),
                "anomalies_detected": sum(
                    1 for e in audit_events if e.get("outcome") == "FAILURE"
                ),
            },
            "record_retention": {
                "records_retained_days": period.days,
                "meets_6_year_requirement": period.days <= 365 * 6,
            },
        }

        findings = self._identify_finra_findings(trade_data, audit_events)
        report = ComplianceReport(
            report_id=report_id,
            regulation="FINRA",
            period=period,
            entity_id=entity_id,
            sections=sections,
            findings=findings,
            attestation=(
                f"This report was generated automatically for {entity_id}. "
                "Manual review and attestation by a compliance officer is required "
                "before submission."
            ),
        )
        self.generated_reports[report_id] = report
        logger.info("FINRA report generated: {} ({})", report_id, period)
        return report

    def generate_mifid2_report(
        self,
        entity_id: str,
        period: ReportPeriod,
        trade_data: list[dict[str, Any]],
    ) -> ComplianceReport:
        """Generate a MiFID2 transaction reporting summary.

        Args:
            entity_id: Entity identifier.
            period: Reporting period.
            trade_data: Trade execution records.

        Returns:
            Generated :class:`ComplianceReport`.
        """
        report_id = self._next_report_id("MiFID2")
        sections = {
            "transaction_report": self._summarise_trades(trade_data),
            "best_execution_policy": {
                "total_executions": len(trade_data),
                "venues": list({t.get("venue", "unknown") for t in trade_data}),
            },
            "pre_trade_transparency": {
                "orders_displayed": len(trade_data),
                "waivers_applied": 0,
            },
            "post_trade_transparency": {
                "reports_submitted": len(trade_data),
                "deferrals": 0,
            },
        }

        report = ComplianceReport(
            report_id=report_id,
            regulation="MiFID2",
            period=period,
            entity_id=entity_id,
            sections=sections,
            findings=[],
            attestation=(
                f"MiFID2 transaction report for {entity_id}. "
                "Requires review by compliance officer before regulatory submission."
            ),
        )
        self.generated_reports[report_id] = report
        logger.info("MiFID2 report generated: {} ({})", report_id, period)
        return report

    def export_json(self, report_id: str) -> str:
        """Export a report as a formatted JSON string.

        Args:
            report_id: Report identifier.

        Returns:
            JSON string representation of the report.

        Raises:
            KeyError: If ``report_id`` is not found.
        """
        if report_id not in self.generated_reports:
            raise KeyError(f"Report '{report_id}' not found")

        report = self.generated_reports[report_id]
        data = {
            "report_id": report.report_id,
            "regulation": report.regulation,
            "period": {"start": str(report.period.start), "end": str(report.period.end)},
            "entity_id": report.entity_id,
            "sections": report.sections,
            "findings": report.findings,
            "attestation": report.attestation,
            "generated_at": report.generated_at.isoformat(),
            "status": report.status,
        }
        return json.dumps(data, indent=2, default=str)

    def finalise(self, report_id: str, officer_name: str) -> ComplianceReport:
        """Mark a report as FINAL with officer attestation.

        Args:
            report_id: Report to finalise.
            officer_name: Name of the attesting compliance officer.

        Returns:
            Updated :class:`ComplianceReport`.

        Raises:
            KeyError: If report not found.
        """
        if report_id not in self.generated_reports:
            raise KeyError(f"Report '{report_id}' not found")

        report = self.generated_reports[report_id]
        report.status = "FINAL"
        report.attestation += f"\n\nAttestation by: {officer_name} on {datetime.now(timezone.utc).isoformat()}"
        logger.info("Report {} finalised by {}", report_id, officer_name)
        return report

    def _next_report_id(self, regulation: str) -> str:
        """Generate the next report identifier.

        Args:
            regulation: Regulation prefix.

        Returns:
            Report ID string.
        """
        self._report_counter += 1
        ts = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"{regulation}-{ts}-{self._report_counter:04d}"

    @staticmethod
    def _summarise_trades(trades: list[dict[str, Any]]) -> dict[str, Any]:
        """Summarise trade data for report sections.

        Args:
            trades: Trade records.

        Returns:
            Summary dictionary.
        """
        if not trades:
            return {"count": 0, "total_value": 0.0, "symbols": []}

        symbols = list({t.get("symbol", "unknown") for t in trades})
        total_value = sum(t.get("quantity", 0) * t.get("price", 0) for t in trades)
        buy_count = sum(1 for t in trades if t.get("direction", "").upper() == "BUY")
        sell_count = len(trades) - buy_count

        return {
            "count": len(trades),
            "total_value": round(total_value, 2),
            "symbols": symbols,
            "buy_count": buy_count,
            "sell_count": sell_count,
        }

    @staticmethod
    def _best_execution_analysis(trades: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyse best execution quality.

        Args:
            trades: Trade records with optional ``"slippage"`` field.

        Returns:
            Best execution metrics.
        """
        slippages = [t.get("slippage", 0.0) for t in trades]
        if not slippages:
            return {"mean_slippage": 0.0, "max_slippage": 0.0}

        import numpy as np
        return {
            "mean_slippage": round(float(np.mean(slippages)), 6),
            "max_slippage": round(float(np.max(slippages)), 6),
            "trades_with_positive_slippage": sum(1 for s in slippages if s > 0),
        }

    @staticmethod
    def _identify_finra_findings(
        trades: list[dict[str, Any]],
        audit_events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Identify potential FINRA compliance findings.

        Args:
            trades: Trade records.
            audit_events: Audit log entries.

        Returns:
            List of finding dictionaries.
        """
        findings: list[dict[str, Any]] = []

        # Check for large trades without pre-approval
        large_trades = [
            t for t in trades
            if t.get("quantity", 0) * t.get("price", 0) > 1_000_000
            and not t.get("pre_approved", False)
        ]
        if large_trades:
            findings.append({
                "finding_id": "FINRA-001",
                "description": f"{len(large_trades)} large trade(s) without pre-approval",
                "severity": "HIGH",
                "trade_ids": [t.get("trade_id") for t in large_trades[:5]],
            })

        # Check for after-hours trades
        after_hours = [
            t for t in trades if t.get("after_hours", False)
        ]
        if after_hours:
            findings.append({
                "finding_id": "FINRA-002",
                "description": f"{len(after_hours)} after-hours trade(s) detected",
                "severity": "MEDIUM",
            })

        return findings
