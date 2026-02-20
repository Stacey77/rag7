"""Dependency vulnerability scanning against a known CVE database."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from loguru import logger


@dataclass
class Vulnerability:
    """A known vulnerability in a dependency.

    Attributes:
        cve_id: CVE identifier (e.g. ``"CVE-2021-12345"``).
        package_name: Affected package name.
        affected_versions: Version range string (e.g. ``"<2.0.0"``).
        severity: CVSS severity (``"CRITICAL"``, ``"HIGH"``, ``"MEDIUM"``, ``"LOW"``).
        cvss_score: CVSS base score (0–10).
        description: Vulnerability description.
        fix_version: Version that resolves the vulnerability.
        references: URLs to advisories.
    """

    cve_id: str
    package_name: str
    affected_versions: str
    severity: str
    cvss_score: float
    description: str
    fix_version: str = ""
    references: list[str] = field(default_factory=list)


@dataclass
class DependencyFinding:
    """A vulnerability finding for a specific installed version.

    Attributes:
        package_name: Package name.
        installed_version: Currently installed version string.
        vulnerability: The matched vulnerability record.
        is_fixed_version_available: Whether a fix is known.
    """

    package_name: str
    installed_version: str
    vulnerability: Vulnerability
    is_fixed_version_available: bool


@dataclass
class DependencyScanResult:
    """Result of a dependency vulnerability scan.

    Attributes:
        scan_id: Unique scan identifier.
        scanned_packages: Total packages evaluated.
        findings: All vulnerability findings.
        critical_count: Number of CRITICAL findings.
        high_count: Number of HIGH findings.
        medium_count: Number of MEDIUM findings.
        low_count: Number of LOW findings.
        scanned_at: UTC timestamp.
    """

    scan_id: str
    scanned_packages: int
    findings: list[DependencyFinding]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def passed(self) -> bool:
        """Whether the scan passed (no CRITICAL or HIGH findings)."""
        return self.critical_count == 0 and self.high_count == 0


# Minimal sample CVE database for demonstration purposes
_SAMPLE_CVE_DB: list[Vulnerability] = [
    Vulnerability(
        cve_id="CVE-2022-42919",
        package_name="cpython",
        affected_versions="<3.11.1",
        severity="HIGH",
        cvss_score=7.8,
        description="Local privilege escalation on Linux via Python's multiprocessing",
        fix_version="3.11.1",
    ),
    Vulnerability(
        cve_id="CVE-2023-24329",
        package_name="urllib3",
        affected_versions="<1.26.15",
        severity="MEDIUM",
        cvss_score=5.3,
        description="urllib3 HTTP request smuggling via crafted scheme",
        fix_version="1.26.15",
    ),
    Vulnerability(
        cve_id="CVE-2022-23491",
        package_name="certifi",
        affected_versions="<2022.12.7",
        severity="MEDIUM",
        cvss_score=6.5,
        description="Certifi includes roots for e-Tugra CA which was revoked",
        fix_version="2022.12.7",
    ),
    Vulnerability(
        cve_id="CVE-2021-33503",
        package_name="urllib3",
        affected_versions="<1.26.5",
        severity="HIGH",
        cvss_score=7.5,
        description="urllib3 ReDoS in authority regex parsing",
        fix_version="1.26.5",
    ),
]


class DependencyScanner:
    """Dependency vulnerability scanner using an abstract CVE interface.

    Scans a list of package–version pairs against a known vulnerability
    database.  In production this would integrate with OSV, NVD, or
    GitHub Advisory Database APIs.

    Attributes:
        _cve_db: Vulnerability database.
        scan_history: All completed scan results.
    """

    def __init__(self, cve_db: list[Vulnerability] | None = None) -> None:
        """Initialise the dependency scanner.

        Args:
            cve_db: Optional custom CVE database; uses built-in sample if None.
        """
        self._cve_db = cve_db or list(_SAMPLE_CVE_DB)
        self.scan_history: list[DependencyScanResult] = []
        logger.info("DependencyScanner initialised ({} CVEs in DB)", len(self._cve_db))

    def add_vulnerability(self, vuln: Vulnerability) -> None:
        """Add a vulnerability to the local CVE database.

        Args:
            vuln: Vulnerability record to add.
        """
        self._cve_db.append(vuln)

    def scan(
        self,
        packages: dict[str, str],
    ) -> DependencyScanResult:
        """Scan installed packages against the CVE database.

        Args:
            packages: Mapping of package name to installed version string.

        Returns:
            :class:`DependencyScanResult` with all findings.
        """
        import time
        scan_id = f"dep_scan_{int(time.time()*1000)}"
        findings: list[DependencyFinding] = []

        for pkg_name, installed_version in packages.items():
            for vuln in self._cve_db:
                if vuln.package_name.lower() == pkg_name.lower():
                    if self._is_affected(installed_version, vuln.affected_versions):
                        is_fixed = bool(vuln.fix_version)
                        findings.append(DependencyFinding(
                            package_name=pkg_name,
                            installed_version=installed_version,
                            vulnerability=vuln,
                            is_fixed_version_available=is_fixed,
                        ))

        critical = sum(1 for f in findings if f.vulnerability.severity == "CRITICAL")
        high = sum(1 for f in findings if f.vulnerability.severity == "HIGH")
        medium = sum(1 for f in findings if f.vulnerability.severity == "MEDIUM")
        low = sum(1 for f in findings if f.vulnerability.severity == "LOW")

        result = DependencyScanResult(
            scan_id=scan_id,
            scanned_packages=len(packages),
            findings=findings,
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
        )
        self.scan_history.append(result)
        logger.info(
            "Dependency scan: {}/{} packages vulnerable (C:{}, H:{}, M:{}, L:{})",
            len(findings),
            len(packages),
            critical,
            high,
            medium,
            low,
        )
        return result

    def _is_affected(self, installed: str, version_constraint: str) -> bool:
        """Determine whether the installed version satisfies a constraint.

        Supports simple constraints: ``<x.y.z``, ``<=x.y.z``, ``>=x.y.z``,
        ``>x.y.z``, ``==x.y.z``.

        Args:
            installed: Installed version string.
            version_constraint: Constraint string.

        Returns:
            ``True`` if the installed version is affected.
        """
        try:
            installed_tuple = self._parse_version(installed)
            for constraint in version_constraint.split(","):
                constraint = constraint.strip()
                if constraint.startswith("<="):
                    target = self._parse_version(constraint[2:])
                    if installed_tuple > target:
                        return False
                elif constraint.startswith("<"):
                    target = self._parse_version(constraint[1:])
                    if installed_tuple >= target:
                        return False
                elif constraint.startswith(">="):
                    target = self._parse_version(constraint[2:])
                    if installed_tuple < target:
                        return False
                elif constraint.startswith(">"):
                    target = self._parse_version(constraint[1:])
                    if installed_tuple <= target:
                        return False
                elif constraint.startswith("=="):
                    target = self._parse_version(constraint[2:])
                    if installed_tuple != target:
                        return False
            return True
        except Exception:
            return False  # Cannot determine — treat as unaffected

    @staticmethod
    def _parse_version(version_str: str) -> tuple[int, ...]:
        """Parse a semantic version string into a comparable tuple.

        Args:
            version_str: Version string (e.g. ``"1.2.3"``).

        Returns:
            Tuple of integers (e.g. ``(1, 2, 3)``).
        """
        parts = version_str.strip().split(".")
        return tuple(int(p) for p in parts if p.isdigit())
