"""Deployment automation for services and models."""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DeploymentTarget:
    name: str = ""
    environment: str = "development"  # development | staging | production
    region: str = "us-east-1"
    cluster: str = ""
    namespace: str = "default"
    replicas: int = 1
    resource_limits: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class DeploymentSpec:
    spec_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = ""
    image: str = ""
    tag: str = "latest"
    target: DeploymentTarget = field(default_factory=DeploymentTarget)
    strategy: str = "rolling"    # rolling | blue_green | canary
    health_check_path: str = "/health"
    rollback_on_failure: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentResult:
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = ""
    environment: str = ""
    status: str = "pending"      # pending | running | success | failed | rolled_back
    strategy: str = ""
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    elapsed_seconds: float = 0.0
    events: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RollingDeployment:
    """Simulates a rolling update deployment strategy."""

    def execute(self, spec: DeploymentSpec) -> List[str]:
        events = []
        replicas = spec.target.replicas
        for i in range(1, replicas + 1):
            events.append(f"Updating replica {i}/{replicas} with {spec.image}:{spec.tag}")
            time.sleep(0.01)  # Simulate rollout time
            events.append(f"Replica {i} health check passed")
        events.append("Rolling update complete")
        return events


class BlueGreenDeployment:
    """Simulates a blue/green deployment strategy."""

    def execute(self, spec: DeploymentSpec) -> List[str]:
        return [
            f"Creating green environment for {spec.service_name}",
            f"Deploying {spec.image}:{spec.tag} to green",
            "Running smoke tests on green environment",
            "Smoke tests passed - switching traffic to green",
            "Blue environment standing by for rollback",
            "Blue/green deployment complete",
        ]


class CanaryDeployment:
    """Simulates canary deployment with traffic shifting."""

    def execute(self, spec: DeploymentSpec) -> List[str]:
        events = []
        for pct in [5, 25, 50, 100]:
            events.append(f"Shifting {pct}% traffic to canary")
            events.append(f"Monitoring error rate at {pct}% (0.1% - healthy)")
            time.sleep(0.01)
        events.append("Canary promotion complete - 100% traffic on new version")
        return events


class HealthChecker:
    """Simulates health check verification post-deployment."""

    def check(self, spec: DeploymentSpec) -> tuple:
        """Returns (healthy: bool, message: str)"""
        path = spec.health_check_path
        service = spec.service_name
        logger.debug("Health checking %s at %s", service, path)
        # Simulate health check
        return True, f"Service {service} at {path} returned 200 OK"


class Deployer:
    """
    Multi-strategy deployment automation with rollback, health checking,
    and deployment history tracking.
    """

    def __init__(self) -> None:
        self._strategies = {
            "rolling": RollingDeployment(),
            "blue_green": BlueGreenDeployment(),
            "canary": CanaryDeployment(),
        }
        self._health_checker = HealthChecker()
        self._history: List[DeploymentResult] = []
        self._rollback_handlers: Dict[str, Callable] = {}
        logger.info("Deployer initialized")

    def register_rollback(self, service_name: str, handler: Callable) -> None:
        self._rollback_handlers[service_name] = handler

    def deploy(self, spec: DeploymentSpec) -> DeploymentResult:
        result = DeploymentResult(
            service_name=spec.service_name,
            environment=spec.target.environment,
            strategy=spec.strategy,
            started_at=datetime.utcnow(),
        )
        result.status = "running"
        start = time.perf_counter()
        logger.info("Deploying %s:%s to %s [%s]",
                    spec.service_name, spec.tag, spec.target.environment, spec.strategy)

        strategy = self._strategies.get(spec.strategy, self._strategies["rolling"])
        try:
            events = strategy.execute(spec)
            result.events.extend(events)

            healthy, msg = self._health_checker.check(spec)
            result.events.append(f"Health check: {msg}")

            if healthy:
                result.status = "success"
                logger.info("Deployment of %s succeeded", spec.service_name)
            else:
                if spec.rollback_on_failure:
                    result.events.append("Health check failed - initiating rollback")
                    self._rollback(spec, result)
                else:
                    result.status = "failed"
        except Exception as exc:
            result.status = "failed"
            result.events.append(f"Deployment error: {exc}")
            logger.error("Deployment failed: %s", exc)

        result.elapsed_seconds = time.perf_counter() - start
        result.finished_at = datetime.utcnow()
        self._history.append(result)
        return result

    def _rollback(self, spec: DeploymentSpec, result: DeploymentResult) -> None:
        handler = self._rollback_handlers.get(spec.service_name)
        if handler:
            try:
                handler(spec)
                result.status = "rolled_back"
                result.events.append("Rollback completed successfully")
            except Exception as exc:
                result.status = "failed"
                result.events.append(f"Rollback failed: {exc}")
        else:
            result.status = "rolled_back"
            result.events.append("Simulated rollback to previous version")

    def get_history(self, service_name: Optional[str] = None) -> List[DeploymentResult]:
        if service_name:
            return [r for r in self._history if r.service_name == service_name]
        return list(self._history)

    def last_deployment(self, service_name: str) -> Optional[DeploymentResult]:
        history = self.get_history(service_name)
        return history[-1] if history else None
