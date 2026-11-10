"""Security testing automation runner for CI/CD pipelines."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from loguru import logger


class TestType(Enum):
    """Categories of security tests."""

    SAST = auto()
    DAST = auto()
    DEPENDENCY_SCAN = auto()
    CONTAINER_SCAN = auto()
    SECRETS_SCAN = auto()
    COMPLIANCE = auto()
    PENETRATION = auto()


@dataclass
class SecurityTestResult:
    """Result of a single security test run.

    Attributes:
        test_id: Unique identifier.
        test_type: Category of test.
        test_name: Human-readable name.
        passed: Whether the test passed.
        findings_count: Number of security findings.
        critical_findings: Number of critical findings.
        details: Supplementary result data.
        duration_ms: Test execution time.
        executed_at: UTC timestamp.
    """

    test_id: str
    test_type: TestType
    test_name: str
    passed: bool
    findings_count: int
    critical_findings: int
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TestSuiteResult:
    """Aggregated result of a security test suite run.

    Attributes:
        suite_id: Unique identifier.
        results: Individual test results.
        passed_count: Tests that passed.
        failed_count: Tests that failed.
        total_critical_findings: Total critical findings across all tests.
        overall_passed: Whether the suite passed.
        duration_ms: Total suite duration.
    """

    suite_id: str
    results: list[SecurityTestResult]
    passed_count: int
    failed_count: int
    total_critical_findings: int
    overall_passed: bool
    duration_ms: float


class TestAutomation:
    """Security testing automation runner for CI/CD integration.

    Orchestrates a suite of security tests and aggregates results
    for use in deployment gate evaluations.

    Attributes:
        test_history: All completed suite results.
        _registered_tests: Registered test functions.
    """

    def __init__(self) -> None:
        """Initialise the test automation runner."""
        self.test_history: list[TestSuiteResult] = []
        self._registered_tests: list[tuple[TestType, str, Any]] = []
        self._suite_counter = 0
        logger.info("TestAutomation runner initialised")

    def register_test(
        self,
        test_type: TestType,
        name: str,
        test_fn: Any,
    ) -> None:
        """Register a security test function.

        Args:
            test_type: Category of test.
            name: Human-readable test name.
            test_fn: Async callable ``(context) → SecurityTestResult``.
        """
        self._registered_tests.append((test_type, name, test_fn))
        logger.debug("Security test '{}' ({}) registered", name, test_type.name)

    async def run_suite(
        self,
        context: dict[str, Any] | None = None,
        test_types: list[TestType] | None = None,
    ) -> TestSuiteResult:
        """Execute all registered (or filtered) security tests.

        Args:
            context: Context data passed to each test.
            test_types: If provided, only tests of these types are run.

        Returns:
            :class:`TestSuiteResult` aggregating all results.
        """
        import time
        self._suite_counter += 1
        suite_id = f"suite_{self._suite_counter:06d}"
        context = context or {}
        start = time.monotonic()

        tests_to_run = [
            (tt, name, fn)
            for tt, name, fn in self._registered_tests
            if test_types is None or tt in test_types
        ]

        if not tests_to_run:
            # Run built-in simulated tests
            tests_to_run = self._default_tests()

        logger.info("Running security test suite {}: {} tests", suite_id, len(tests_to_run))
        results: list[SecurityTestResult] = []

        for test_type, name, test_fn in tests_to_run:
            result = await self._run_test(test_type, name, test_fn, context)
            results.append(result)

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        critical = sum(r.critical_findings for r in results)
        duration_ms = (time.monotonic() - start) * 1000

        suite = TestSuiteResult(
            suite_id=suite_id,
            results=results,
            passed_count=passed,
            failed_count=failed,
            total_critical_findings=critical,
            overall_passed=critical == 0,
            duration_ms=round(duration_ms, 2),
        )
        self.test_history.append(suite)
        log = logger.info if suite.overall_passed else logger.error
        log(
            "Suite {}: {}/{} passed, {} critical findings",
            suite_id,
            passed,
            len(results),
            critical,
        )
        return suite

    async def _run_test(
        self,
        test_type: TestType,
        name: str,
        test_fn: Any,
        context: dict[str, Any],
    ) -> SecurityTestResult:
        """Execute a single test with timing.

        Args:
            test_type: Test category.
            name: Test name.
            test_fn: Async callable.
            context: Test context.

        Returns:
            :class:`SecurityTestResult`.
        """
        import time
        test_id = f"test_{hash(name) % 100000:05d}"
        start = time.monotonic()

        try:
            result: SecurityTestResult = await test_fn(context)
            result.duration_ms = round((time.monotonic() - start) * 1000, 2)
            return result
        except Exception as exc:
            logger.error("Test '{}' raised: {}", name, exc)
            return SecurityTestResult(
                test_id=test_id,
                test_type=test_type,
                test_name=name,
                passed=False,
                findings_count=0,
                critical_findings=1,
                details={"error": str(exc)},
                duration_ms=round((time.monotonic() - start) * 1000, 2),
            )

    def _default_tests(self) -> list[tuple[TestType, str, Any]]:
        """Return a set of built-in simulated security tests.

        Returns:
            List of ``(TestType, name, handler)`` tuples.
        """
        async def sast_test(ctx: dict[str, Any]) -> SecurityTestResult:
            await asyncio.sleep(0)
            return SecurityTestResult(
                test_id="sast_001",
                test_type=TestType.SAST,
                test_name="SAST Scan (simulated)",
                passed=True,
                findings_count=2,
                critical_findings=0,
                details={"tool": "simulated"},
            )

        async def dep_test(ctx: dict[str, Any]) -> SecurityTestResult:
            await asyncio.sleep(0)
            return SecurityTestResult(
                test_id="dep_001",
                test_type=TestType.DEPENDENCY_SCAN,
                test_name="Dependency Scan (simulated)",
                passed=True,
                findings_count=1,
                critical_findings=0,
                details={"tool": "simulated"},
            )

        return [
            (TestType.SAST, "SAST Scan", sast_test),
            (TestType.DEPENDENCY_SCAN, "Dependency Scan", dep_test),
        ]
