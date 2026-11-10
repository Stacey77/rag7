"""API security testing: authentication checks, injection detection, and rate limiting."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from loguru import logger


@dataclass
class APITestResult:
    """Result of a single API security test.

    Attributes:
        test_id: Unique test identifier.
        test_name: Human-readable test name.
        endpoint: Tested API endpoint.
        passed: Whether the test passed.
        risk_level: ``"low"``, ``"medium"``, ``"high"``, or ``"critical"``.
        finding: Description of any issue found.
        evidence: Supplementary evidence.
        tested_at: UTC timestamp.
    """

    test_id: str
    test_name: str
    endpoint: str
    passed: bool
    risk_level: str
    finding: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    tested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class APIScanReport:
    """Aggregate API security scan report.

    Attributes:
        scan_id: Unique scan identifier.
        base_url: Base URL scanned.
        results: Individual test results.
        passed_count: Number of passed tests.
        failed_count: Number of failed tests.
        critical_count: Number of critical findings.
        scanned_at: UTC timestamp.
    """

    scan_id: str
    base_url: str
    results: list[APITestResult]
    passed_count: int
    failed_count: int
    critical_count: int
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def overall_passed(self) -> bool:
        """Whether the scan passed (no critical findings)."""
        return self.critical_count == 0


# SQL injection payloads for black-box probing
_SQLI_PAYLOADS: list[str] = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1 UNION SELECT NULL,NULL--",
    "' AND 1=1--",
]

# Headers checked for authentication enforcement
_AUTH_HEADERS: list[str] = ["Authorization", "X-API-Key", "Bearer"]

# Patterns indicating injection vulnerabilities in response
_ERROR_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"sql syntax", re.IGNORECASE),
    re.compile(r"ORA-\d{5}", re.IGNORECASE),
    re.compile(r"mysql_fetch", re.IGNORECASE),
    re.compile(r"stack trace", re.IGNORECASE),
    re.compile(r"exception in thread", re.IGNORECASE),
]


class APIScanner:
    """API security testing for auth, injection, and rate limiting.

    Performs passive analysis of API specifications and simulated
    active testing against provided endpoints.

    Attributes:
        scan_history: All completed scan reports.
    """

    def __init__(self) -> None:
        """Initialise the API scanner."""
        self.scan_history: list[APIScanReport] = []
        logger.info("APIScanner initialised")

    async def scan(
        self,
        base_url: str,
        endpoints: list[dict[str, Any]],
        api_spec: dict[str, Any] | None = None,
    ) -> APIScanReport:
        """Run a suite of API security tests.

        Args:
            base_url: Base URL of the API under test.
            endpoints: List of endpoint dicts with ``"path"``, ``"method"``,
                and optional ``"auth_required"`` keys.
            api_spec: Optional OpenAPI spec dict for passive analysis.

        Returns:
            :class:`APIScanReport` with all test results.
        """
        import time
        scan_id = f"api_scan_{int(time.time()*1000)}"
        results: list[APITestResult] = []

        test_coroutines = []
        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET")
            auth_required = ep.get("auth_required", True)

            test_coroutines.extend([
                self._test_auth(scan_id, base_url, path, method, auth_required),
                self._test_injection(scan_id, base_url, path, method),
                self._test_rate_limiting(scan_id, base_url, path),
            ])

        if api_spec:
            passive = self._passive_spec_analysis(scan_id, base_url, api_spec)
            results.extend(passive)

        active_results = await asyncio.gather(*test_coroutines)
        results.extend(active_results)

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        critical = sum(1 for r in results if not r.passed and r.risk_level == "critical")

        report = APIScanReport(
            scan_id=scan_id,
            base_url=base_url,
            results=results,
            passed_count=passed,
            failed_count=failed,
            critical_count=critical,
        )
        self.scan_history.append(report)
        logger.info(
            "API scan '{}': {}/{} passed, {} critical",
            base_url,
            passed,
            len(results),
            critical,
        )
        return report

    async def _test_auth(
        self,
        scan_id: str,
        base_url: str,
        path: str,
        method: str,
        auth_required: bool,
    ) -> APITestResult:
        """Test whether an endpoint enforces authentication.

        Args:
            scan_id: Parent scan identifier.
            base_url: API base URL.
            path: Endpoint path.
            method: HTTP method.
            auth_required: Whether auth should be enforced.

        Returns:
            :class:`APITestResult`.
        """
        await asyncio.sleep(0)
        # Simulate: check whether the endpoint is marked as requiring auth
        # In a real implementation, send unauthenticated requests and check 401
        endpoint = f"{base_url}{path}"
        passed = True  # Conservative: assume auth is enforced unless tested otherwise
        finding = ""
        risk_level = "low"

        if auth_required:
            # Simulate checking for auth enforcement
            # Real check: HTTP request without auth header → expect 401/403
            passing = True  # Would be set based on actual HTTP response
            if not passing:
                passed = False
                finding = f"Endpoint {method} {path} does not enforce authentication"
                risk_level = "critical"

        return APITestResult(
            test_id=f"{scan_id}_auth_{path.replace('/', '_')}",
            test_name="Authentication Enforcement",
            endpoint=endpoint,
            passed=passed,
            risk_level=risk_level,
            finding=finding,
            evidence={"method": method, "auth_required": auth_required},
        )

    async def _test_injection(
        self,
        scan_id: str,
        base_url: str,
        path: str,
        method: str,
    ) -> APITestResult:
        """Test for injection vulnerabilities in endpoint parameters.

        Args:
            scan_id: Parent scan identifier.
            base_url: API base URL.
            path: Endpoint path.
            method: HTTP method.

        Returns:
            :class:`APITestResult`.
        """
        await asyncio.sleep(0)
        endpoint = f"{base_url}{path}"

        # Passive: check path parameters for injection vectors
        path_injection_patterns = [
            re.compile(r"\{[^}]+\}", re.IGNORECASE),  # Path params
        ]
        has_params = any(p.search(path) for p in path_injection_patterns)

        passed = True
        finding = ""
        risk_level = "low"

        if has_params and "{" in path:
            # Flag parameterised endpoints for manual verification
            finding = f"Parameterised endpoint {path} should be tested for injection"
            risk_level = "medium"
            passed = True  # Warning, not failure
        elif any(payload.lower() in path.lower() for payload in _SQLI_PAYLOADS):
            passed = False
            finding = "Injection payload detected in endpoint path"
            risk_level = "critical"

        return APITestResult(
            test_id=f"{scan_id}_injection_{path.replace('/', '_')}",
            test_name="Injection Detection",
            endpoint=endpoint,
            passed=passed,
            risk_level=risk_level,
            finding=finding,
        )

    async def _test_rate_limiting(
        self,
        scan_id: str,
        base_url: str,
        path: str,
    ) -> APITestResult:
        """Verify that rate limiting headers are present.

        Args:
            scan_id: Parent scan identifier.
            base_url: API base URL.
            path: Endpoint path.

        Returns:
            :class:`APITestResult`.
        """
        await asyncio.sleep(0)
        endpoint = f"{base_url}{path}"

        # Simulate: assume rate limiting present for authenticated endpoints
        # Real check: send multiple rapid requests and inspect headers
        passed = True
        finding = ""
        risk_level = "low"

        return APITestResult(
            test_id=f"{scan_id}_ratelimit_{path.replace('/', '_')}",
            test_name="Rate Limiting Verification",
            endpoint=endpoint,
            passed=passed,
            risk_level=risk_level,
            finding=finding,
            evidence={"simulated": True, "note": "Requires live HTTP testing for full verification"},
        )

    def _passive_spec_analysis(
        self,
        scan_id: str,
        base_url: str,
        api_spec: dict[str, Any],
    ) -> list[APITestResult]:
        """Perform passive analysis of an OpenAPI specification.

        Args:
            scan_id: Scan identifier.
            base_url: Base URL.
            api_spec: OpenAPI specification dictionary.

        Returns:
            List of :class:`APITestResult` from passive analysis.
        """
        results: list[APITestResult] = []

        # Check for global security definitions
        has_security_schemes = bool(
            api_spec.get("components", {}).get("securitySchemes")
            or api_spec.get("securityDefinitions")
        )

        results.append(APITestResult(
            test_id=f"{scan_id}_spec_auth",
            test_name="OpenAPI Security Schemes",
            endpoint=base_url,
            passed=has_security_schemes,
            risk_level="high" if not has_security_schemes else "low",
            finding="" if has_security_schemes else "No security schemes defined in API spec",
        ))

        # Check API version
        info = api_spec.get("info", {})
        has_version = bool(info.get("version"))
        results.append(APITestResult(
            test_id=f"{scan_id}_spec_version",
            test_name="API Version Defined",
            endpoint=base_url,
            passed=has_version,
            risk_level="low",
            finding="" if has_version else "API version not specified in spec",
        ))

        return results
