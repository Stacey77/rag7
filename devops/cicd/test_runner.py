"""Automated testing framework."""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    test_type: str = "unit"   # unit | integration | e2e | smoke | performance
    func: Optional[Callable] = None
    timeout_seconds: int = 60
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    test_id: str = ""
    name: str = ""
    status: str = "pending"    # passed | failed | error | skipped | timeout
    elapsed_ms: float = 0.0
    error_message: str = ""
    stdout: str = ""
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


@dataclass
class TestSuiteResult:
    suite_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    suite_name: str = ""
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    results: List[TestResult] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    @property
    def pass_rate(self) -> float:
        return self.passed / max(self.total, 1)

    @property
    def success(self) -> bool:
        return self.failed == 0 and self.errors == 0


class TestRunner:
    """
    Automated test runner with test registration, execution,
    parallel grouping, and rich reporting.
    """

    def __init__(self) -> None:
        self._suites: Dict[str, List[TestCase]] = {}
        self._global_fixtures: Dict[str, Any] = {}
        logger.info("TestRunner initialized")

    def register(self, suite: str, test_case: TestCase) -> None:
        self._suites.setdefault(suite, []).append(test_case)

    def test(self, suite: str, name: str, test_type: str = "unit",
             tags: Optional[List[str]] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            tc = TestCase(name=name, test_type=test_type, func=func, tags=tags or [])
            self.register(suite, tc)
            return func
        return decorator

    def add_fixture(self, name: str, value: Any) -> None:
        self._global_fixtures[name] = value

    def _run_test(self, tc: TestCase) -> TestResult:
        result = TestResult(test_id=tc.test_id, name=tc.name, started_at=datetime.utcnow())
        start = time.perf_counter()
        if tc.func is None:
            result.status = "skipped"
        else:
            try:
                import signal
                tc.func(**{k: v for k, v in self._global_fixtures.items()
                            if k in (tc.func.__code__.co_varnames if tc.func else [])})
                result.status = "passed"
            except AssertionError as e:
                result.status = "failed"
                result.error_message = str(e)
            except Exception as e:
                result.status = "error"
                result.error_message = f"{type(e).__name__}: {e}"
        result.elapsed_ms = (time.perf_counter() - start) * 1000
        result.finished_at = datetime.utcnow()
        return result

    def run_suite(self, suite_name: str,
                  tags: Optional[List[str]] = None,
                  test_type: Optional[str] = None) -> TestSuiteResult:
        tests = self._suites.get(suite_name, [])
        if tags:
            tests = [t for t in tests if any(tag in t.tags for tag in tags)]
        if test_type:
            tests = [t for t in tests if t.test_type == test_type]

        suite_result = TestSuiteResult(suite_name=suite_name,
                                        total=len(tests),
                                        started_at=datetime.utcnow())
        start = time.perf_counter()
        for tc in tests:
            result = self._run_test(tc)
            suite_result.results.append(result)
            if result.status == "passed":
                suite_result.passed += 1
            elif result.status == "failed":
                suite_result.failed += 1
            elif result.status == "error":
                suite_result.errors += 1
            elif result.status == "skipped":
                suite_result.skipped += 1
            logger.debug("[%s] %s: %s (%.1fms)", suite_name, tc.name, result.status, result.elapsed_ms)

        suite_result.elapsed_seconds = time.perf_counter() - start
        suite_result.finished_at = datetime.utcnow()
        logger.info("Suite '%s': %d/%d passed (%.1fs)",
                    suite_name, suite_result.passed, suite_result.total, suite_result.elapsed_seconds)
        return suite_result

    def run_all(self) -> Dict[str, TestSuiteResult]:
        return {suite: self.run_suite(suite) for suite in self._suites}

    def report(self, result: TestSuiteResult) -> str:
        lines = [
            f"Test Suite: {result.suite_name}",
            f"Total: {result.total} | Passed: {result.passed} | Failed: {result.failed} | "
            f"Errors: {result.errors} | Skipped: {result.skipped}",
            f"Pass rate: {result.pass_rate:.1%} | Duration: {result.elapsed_seconds:.2f}s",
            "",
        ]
        for r in result.results:
            status_icon = {"passed": "✓", "failed": "✗", "error": "!", "skipped": "-"}.get(r.status, "?")
            line = f"  {status_icon} {r.name} ({r.elapsed_ms:.1f}ms)"
            if r.error_message:
                line += f"\n      {r.error_message}"
            lines.append(line)
        return "\n".join(lines)
