"""Bridge the AI platform with DevOps tooling (deployments, tests, metrics, scaling)."""

import logging
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

HEALTHY_THRESHOLD = 0.9      # health score >= this → "healthy"
DEGRADED_THRESHOLD = 0.6     # health score >= this → "degraded"


class DevOpsBridge:
    """Simulate DevOps operations: deployments, test runs, metric collection, scaling."""

    def __init__(self) -> None:
        # service -> {version, environment, deployed_at, replicas}
        self._deployments: Dict[str, Dict[str, Any]] = {}
        # service -> list of metric snapshots
        self._metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # suite -> list of test results
        self._test_results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        logger.info("DevOpsBridge initialised.")

    def trigger_deployment(self, service: str, version: str, environment: str) -> Dict[str, Any]:
        """Simulate deploying *service* at *version* to *environment*."""
        t0 = time.monotonic()
        # Simulate deployment latency
        success = random.random() > 0.05  # 95 % success rate
        latency_ms = round((time.monotonic() - t0) * 1000 + random.uniform(200, 800), 2)
        record = {
            "service": service, "version": version, "environment": environment,
            "success": success, "latency_ms": latency_ms,
            "deployed_at": datetime.utcnow().isoformat(),
        }
        if success:
            self._deployments[service] = record
            logger.info("Deployed %s@%s to %s", service, version, environment)
        else:
            logger.error("Deployment failed: %s@%s → %s", service, version, environment)
        return record

    def run_tests(self, suite_name: str) -> Dict[str, Any]:
        """Execute a named test suite (simulated) and return results."""
        t0 = time.monotonic()
        total = random.randint(20, 100)
        failed = random.randint(0, max(1, total // 20))
        skipped = random.randint(0, max(1, total // 10))
        passed = total - failed - skipped
        latency_ms = round((time.monotonic() - t0) * 1000 + random.uniform(500, 3000), 2)
        result = {
            "suite": suite_name, "total": total, "passed": passed,
            "failed": failed, "skipped": skipped,
            "success": failed == 0, "latency_ms": latency_ms,
            "run_at": datetime.utcnow().isoformat(),
        }
        self._test_results[suite_name].append(result)
        logger.info("Test suite '%s': %d/%d passed", suite_name, passed, total)
        return result

    def collect_metrics(self, service: str) -> Dict[str, Any]:
        """Simulate collecting runtime metrics for *service*."""
        snapshot = {
            "service": service,
            "cpu_pct": round(random.uniform(5, 85), 1),
            "memory_pct": round(random.uniform(20, 90), 1),
            "request_rate_rps": round(random.uniform(1, 500), 1),
            "error_rate_pct": round(random.uniform(0, 5), 2),
            "p99_latency_ms": round(random.uniform(50, 2000), 1),
            "collected_at": datetime.utcnow().isoformat(),
        }
        self._metrics[service].append(snapshot)
        logger.debug("Metrics collected for %s: cpu=%.1f%%", service, snapshot["cpu_pct"])
        return snapshot

    def check_health(self, service: str) -> Dict[str, Any]:
        """Derive a health status from recent metrics for *service*."""
        recent = self._metrics.get(service, [])
        if not recent:
            # No data — collect now
            self.collect_metrics(service)
            recent = self._metrics[service]

        latest = recent[-1]
        score = 1.0
        score -= max(0, (latest["cpu_pct"] - 70) / 100)
        score -= max(0, (latest["memory_pct"] - 75) / 100)
        score -= latest["error_rate_pct"] / 10
        score = round(max(0.0, min(1.0, score)), 3)

        if score >= HEALTHY_THRESHOLD:
            status = "healthy"
        elif score >= DEGRADED_THRESHOLD:
            status = "degraded"
        else:
            status = "unhealthy"

        deployment = self._deployments.get(service, {})
        return {
            "service": service, "status": status, "health_score": score,
            "version": deployment.get("version", "unknown"),
            "environment": deployment.get("environment", "unknown"),
            "metrics": latest,
        }

    def auto_scale(self, service: str, target_replicas: int) -> bool:
        """Simulate a scaling operation for *service*."""
        target_replicas = max(1, min(target_replicas, 50))
        if service in self._deployments:
            self._deployments[service]["replicas"] = target_replicas
            logger.info("Auto-scaled %s to %d replicas.", service, target_replicas)
            return True
        logger.warning("Cannot scale unknown service: %s", service)
        return False
