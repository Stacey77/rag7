"""Static application security testing (SAST) wrapper using bandit."""

from __future__ import annotations

import subprocess
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from loguru import logger


@dataclass
class CodeIssue:
    """A security issue detected by static analysis.

    Attributes:
        issue_id: Unique identifier.
        severity: Severity level (``"LOW"``, ``"MEDIUM"``, ``"HIGH"``).
        confidence: Detection confidence (``"LOW"``, ``"MEDIUM"``, ``"HIGH"``).
        issue_type: Issue category (e.g. ``"B601"``, ``"hardcoded_password"``).
        description: Human-readable description.
        file_path: Source file containing the issue.
        line_number: Line number of the issue.
        code_snippet: Offending code excerpt.
        cwe: Common Weakness Enumeration identifier (e.g. ``"CWE-89"``).
    """

    issue_id: str
    severity: str
    confidence: str
    issue_type: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str = ""
    cwe: str = ""


@dataclass
class ScanResult:
    """Result of a code security scan.

    Attributes:
        scan_id: Unique scan identifier.
        target_path: Path that was scanned.
        issues: Detected security issues.
        high_count: Number of HIGH severity issues.
        medium_count: Number of MEDIUM severity issues.
        low_count: Number of LOW severity issues.
        tool: Scanner tool used.
        scan_duration_ms: Time taken for the scan.
        scanned_at: UTC timestamp.
    """

    scan_id: str
    target_path: str
    issues: list[CodeIssue]
    high_count: int
    medium_count: int
    low_count: int
    tool: str
    scan_duration_ms: float
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def passed(self) -> bool:
        """Whether the scan passed (no HIGH severity issues)."""
        return self.high_count == 0


class CodeScanner:
    """SAST wrapper that runs bandit if available, with an abstract fallback.

    When bandit is not installed, the scanner returns an abstract result
    indicating that a real scan was not performed.

    Attributes:
        _bandit_available: Whether the bandit binary is accessible.
        scan_history: Log of all scan results.
    """

    def __init__(self) -> None:
        """Initialise the code scanner and probe for bandit availability."""
        self.scan_history: list[ScanResult] = []
        self._bandit_available = self._check_bandit()
        if self._bandit_available:
            logger.info("CodeScanner initialised (bandit available)")
        else:
            logger.warning(
                "CodeScanner initialised — bandit not found. "
                "Install with: pip install bandit"
            )

    def scan(
        self,
        target_path: str,
        severity_level: str = "LOW",
        confidence_level: str = "LOW",
    ) -> ScanResult:
        """Run a static security scan on the target path.

        Uses bandit when available; falls back to an abstract stub result.

        Args:
            target_path: File or directory to scan.
            severity_level: Minimum severity to report (``"LOW"``, ``"MEDIUM"``,
                ``"HIGH"``).
            confidence_level: Minimum confidence to report.

        Returns:
            :class:`ScanResult` with detected issues.
        """
        import time
        start = time.monotonic()
        scan_id = f"scan_{int(time.time()*1000)}"

        if self._bandit_available:
            result = self._run_bandit(target_path, severity_level, confidence_level, scan_id)
        else:
            result = self._abstract_result(target_path, scan_id)

        result.scan_duration_ms = round((time.monotonic() - start) * 1000, 2)
        self.scan_history.append(result)
        logger.info(
            "Code scan '{}': {} issues (H:{}, M:{}, L:{})",
            target_path,
            len(result.issues),
            result.high_count,
            result.medium_count,
            result.low_count,
        )
        return result

    def _run_bandit(
        self,
        target_path: str,
        severity_level: str,
        confidence_level: str,
        scan_id: str,
    ) -> ScanResult:
        """Execute bandit and parse its JSON output.

        Args:
            target_path: Path to scan.
            severity_level: Minimum severity filter.
            confidence_level: Minimum confidence filter.
            scan_id: Scan identifier.

        Returns:
            Parsed :class:`ScanResult`.
        """
        try:
            proc = subprocess.run(
                [
                    "bandit",
                    "-r",
                    target_path,
                    "-f",
                    "json",
                    "-l",
                    severity_level[0].lower(),
                    "-i",
                    confidence_level[0].lower(),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            data = json.loads(proc.stdout or "{}")
            return self._parse_bandit_output(data, target_path, scan_id)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as exc:
            logger.error("Bandit execution error: {}", exc)
            return self._abstract_result(target_path, scan_id, error=str(exc))

    def _parse_bandit_output(
        self,
        data: dict[str, Any],
        target_path: str,
        scan_id: str,
    ) -> ScanResult:
        """Parse bandit JSON output into a ScanResult.

        Args:
            data: Bandit JSON output dictionary.
            target_path: Scanned path.
            scan_id: Scan identifier.

        Returns:
            Populated :class:`ScanResult`.
        """
        issues: list[CodeIssue] = []
        raw_results = data.get("results", [])

        for i, r in enumerate(raw_results):
            issues.append(CodeIssue(
                issue_id=f"{scan_id}_{i:04d}",
                severity=r.get("issue_severity", "UNDEFINED").upper(),
                confidence=r.get("issue_confidence", "UNDEFINED").upper(),
                issue_type=r.get("test_id", ""),
                description=r.get("issue_text", ""),
                file_path=r.get("filename", ""),
                line_number=r.get("line_number", 0),
                code_snippet=r.get("code", ""),
                cwe=r.get("issue_cwe", {}).get("id", "") if isinstance(r.get("issue_cwe"), dict) else "",
            ))

        high = sum(1 for i in issues if i.severity == "HIGH")
        medium = sum(1 for i in issues if i.severity == "MEDIUM")
        low = sum(1 for i in issues if i.severity == "LOW")

        return ScanResult(
            scan_id=scan_id,
            target_path=target_path,
            issues=issues,
            high_count=high,
            medium_count=medium,
            low_count=low,
            tool="bandit",
            scan_duration_ms=0.0,
        )

    def _abstract_result(
        self,
        target_path: str,
        scan_id: str,
        error: str = "",
    ) -> ScanResult:
        """Return a stub result when bandit is unavailable.

        Args:
            target_path: Path that would have been scanned.
            scan_id: Scan identifier.
            error: Optional error message.

        Returns:
            Stub :class:`ScanResult` with no issues detected.
        """
        logger.warning("Abstract scan result returned for '{}' (bandit unavailable)", target_path)
        return ScanResult(
            scan_id=scan_id,
            target_path=target_path,
            issues=[],
            high_count=0,
            medium_count=0,
            low_count=0,
            tool="abstract" if not error else "error",
            scan_duration_ms=0.0,
        )

    @staticmethod
    def _check_bandit() -> bool:
        """Probe whether bandit is installed and accessible.

        Returns:
            ``True`` if bandit is available.
        """
        try:
            result = subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
