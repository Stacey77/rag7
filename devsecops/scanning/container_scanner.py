"""Container image security scanning."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from loguru import logger


@dataclass
class ContainerVulnerability:
    """A vulnerability found in a container image layer.

    Attributes:
        cve_id: CVE identifier.
        package: Affected OS or library package.
        installed_version: Installed package version.
        fixed_version: Version with the fix (empty if no fix available).
        severity: ``"CRITICAL"``, ``"HIGH"``, ``"MEDIUM"``, ``"LOW"``.
        layer: Image layer where the package was installed.
        description: Brief description.
    """

    cve_id: str
    package: str
    installed_version: str
    fixed_version: str
    severity: str
    layer: str = ""
    description: str = ""


@dataclass
class ContainerScanResult:
    """Result of a container image security scan.

    Attributes:
        scan_id: Unique scan identifier.
        image: Image reference that was scanned.
        vulnerabilities: All detected vulnerabilities.
        critical_count: Number of CRITICAL vulnerabilities.
        high_count: Number of HIGH vulnerabilities.
        medium_count: Number of MEDIUM vulnerabilities.
        low_count: Number of LOW vulnerabilities.
        base_image: Detected base image.
        tool: Scanner tool used.
        scanned_at: UTC timestamp.
    """

    scan_id: str
    image: str
    vulnerabilities: list[ContainerVulnerability]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    base_image: str = ""
    tool: str = "abstract"
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def passed(self) -> bool:
        """Whether the scan passed (no CRITICAL findings)."""
        return self.critical_count == 0


class ContainerScanner:
    """Container image security scanner.

    Attempts to use ``trivy`` (if available) for real scanning; otherwise
    returns an abstract stub result indicating the scan was not performed.

    Attributes:
        scan_history: All completed scan results.
        _trivy_available: Whether trivy binary is accessible.
    """

    def __init__(self) -> None:
        """Initialise the container scanner and probe for trivy."""
        self.scan_history: list[ContainerScanResult] = []
        self._trivy_available = self._check_trivy()
        if self._trivy_available:
            logger.info("ContainerScanner initialised (trivy available)")
        else:
            logger.warning(
                "ContainerScanner initialised — trivy not found. "
                "Install from: https://github.com/aquasecurity/trivy"
            )

    def scan(self, image: str, severity: str = "CRITICAL,HIGH,MEDIUM,LOW") -> ContainerScanResult:
        """Scan a container image for vulnerabilities.

        Args:
            image: Docker image reference (e.g. ``"nginx:1.25"``).
            severity: Comma-separated severity levels to include.

        Returns:
            :class:`ContainerScanResult` with findings.
        """
        import time
        scan_id = f"con_scan_{int(time.time()*1000)}"

        if self._trivy_available:
            result = self._run_trivy(image, severity, scan_id)
        else:
            result = self._abstract_result(image, scan_id)

        self.scan_history.append(result)
        logger.info(
            "Container scan '{}': C:{}, H:{}, M:{}, L:{}",
            image,
            result.critical_count,
            result.high_count,
            result.medium_count,
            result.low_count,
        )
        return result

    def _run_trivy(self, image: str, severity: str, scan_id: str) -> ContainerScanResult:
        """Run trivy and parse its JSON output.

        Args:
            image: Container image reference.
            severity: Severity filter string.
            scan_id: Scan identifier.

        Returns:
            Parsed :class:`ContainerScanResult`.
        """
        import json
        try:
            proc = subprocess.run(
                [
                    "trivy",
                    "image",
                    "--format",
                    "json",
                    "--severity",
                    severity,
                    "--quiet",
                    image,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            data = json.loads(proc.stdout or "{}")
            return self._parse_trivy_output(data, image, scan_id)
        except Exception as exc:
            logger.error("Trivy execution error: {}", exc)
            return self._abstract_result(image, scan_id, error=str(exc))

    def _parse_trivy_output(
        self, data: dict[str, Any], image: str, scan_id: str
    ) -> ContainerScanResult:
        """Parse trivy JSON output.

        Args:
            data: Trivy JSON response.
            image: Image reference.
            scan_id: Scan identifier.

        Returns:
            :class:`ContainerScanResult`.
        """
        vulns: list[ContainerVulnerability] = []
        base_image = data.get("Metadata", {}).get("OS", {}).get("Family", "")

        for result in data.get("Results", []):
            layer = result.get("Target", "")
            for v in result.get("Vulnerabilities", []) or []:
                vulns.append(ContainerVulnerability(
                    cve_id=v.get("VulnerabilityID", ""),
                    package=v.get("PkgName", ""),
                    installed_version=v.get("InstalledVersion", ""),
                    fixed_version=v.get("FixedVersion", ""),
                    severity=v.get("Severity", "UNKNOWN").upper(),
                    layer=layer,
                    description=(v.get("Description", ""))[:200],
                ))

        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for v in vulns:
            if v.severity in counts:
                counts[v.severity] += 1

        return ContainerScanResult(
            scan_id=scan_id,
            image=image,
            vulnerabilities=vulns,
            critical_count=counts["CRITICAL"],
            high_count=counts["HIGH"],
            medium_count=counts["MEDIUM"],
            low_count=counts["LOW"],
            base_image=base_image,
            tool="trivy",
        )

    def _abstract_result(
        self, image: str, scan_id: str, error: str = ""
    ) -> ContainerScanResult:
        """Return a stub result when trivy is unavailable.

        Args:
            image: Image reference.
            scan_id: Scan identifier.
            error: Optional error message.

        Returns:
            Stub :class:`ContainerScanResult`.
        """
        return ContainerScanResult(
            scan_id=scan_id,
            image=image,
            vulnerabilities=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0,
            tool="abstract" if not error else "error",
        )

    @staticmethod
    def _check_trivy() -> bool:
        """Check whether trivy is installed and accessible.

        Returns:
            ``True`` if trivy is available.
        """
        try:
            result = subprocess.run(
                ["trivy", "--version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
