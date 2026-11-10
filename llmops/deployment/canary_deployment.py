"""Canary deployment manager for safe LLM rollouts."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class DeploymentState(Enum):
    """Lifecycle states of a canary deployment."""

    PENDING = auto()
    CANARY = auto()
    PROMOTING = auto()
    STABLE = auto()
    ROLLING_BACK = auto()
    ROLLED_BACK = auto()
    FAILED = auto()


@dataclass
class CanaryConfig:
    """Configuration for a canary deployment.

    Attributes:
        deployment_id: Unique identifier for the deployment.
        model_id: Identifier of the new model version being deployed.
        baseline_model_id: Identifier of the stable baseline model.
        initial_traffic_pct: Starting traffic percentage for canary (0–100).
        max_traffic_pct: Maximum traffic percentage for canary before promotion.
        error_rate_threshold: Error rate above which auto-rollback triggers.
        latency_threshold_ms: Latency above which auto-rollback triggers.
        observation_window_s: Seconds to observe before promotion decisions.
    """

    deployment_id: str
    model_id: str
    baseline_model_id: str
    initial_traffic_pct: float = 5.0
    max_traffic_pct: float = 50.0
    error_rate_threshold: float = 0.05
    latency_threshold_ms: float = 500.0
    observation_window_s: float = 60.0


@dataclass
class CanaryMetrics:
    """Real-time metrics snapshot for a canary deployment.

    Attributes:
        deployment_id: Owning deployment identifier.
        error_rate: Fraction of requests that errored.
        p50_latency_ms: 50th percentile latency.
        p99_latency_ms: 99th percentile latency.
        requests_served: Total requests handled by the canary.
        timestamp: UTC time of the snapshot.
    """

    deployment_id: str
    error_rate: float
    p50_latency_ms: float
    p99_latency_ms: float
    requests_served: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CanaryDeployment:
    """Safe canary rollout manager for LLM model versions.

    Manages traffic shifting, metric monitoring, and automated
    promotion or rollback decisions.

    Attributes:
        deployments: Active and completed deployments keyed by ID.
        _metrics_history: Per-deployment metric snapshots.
        _states: Current lifecycle state per deployment.
    """

    def __init__(self) -> None:
        """Initialise the canary deployment manager."""
        self.deployments: dict[str, CanaryConfig] = {}
        self._metrics_history: dict[str, list[CanaryMetrics]] = {}
        self._states: dict[str, DeploymentState] = {}
        logger.info("CanaryDeployment manager initialised")

    def deploy_canary(self, config: CanaryConfig) -> str:
        """Register and activate a new canary deployment.

        Args:
            config: Canary deployment configuration.

        Returns:
            Deployment identifier.

        Raises:
            ValueError: If traffic percentages are out of range.
            ValueError: If a deployment with the same ID already exists.
        """
        if not 0 < config.initial_traffic_pct < 100:
            raise ValueError(
                f"initial_traffic_pct must be in (0, 100), got {config.initial_traffic_pct}"
            )
        if config.initial_traffic_pct > config.max_traffic_pct:
            raise ValueError(
                "initial_traffic_pct must not exceed max_traffic_pct"
            )
        if config.deployment_id in self.deployments:
            raise ValueError(f"Deployment '{config.deployment_id}' already exists")

        self.deployments[config.deployment_id] = config
        self._metrics_history[config.deployment_id] = []
        self._states[config.deployment_id] = DeploymentState.CANARY

        logger.info(
            "Canary deployed: model='{}' at {:.0f}% traffic (id={})",
            config.model_id,
            config.initial_traffic_pct,
            config.deployment_id,
        )
        return config.deployment_id

    async def monitor_metrics(
        self,
        deployment_id: str,
        n_samples: int = 50,
    ) -> CanaryMetrics:
        """Collect and record a metrics snapshot for the canary.

        In production this would query observability infrastructure; here
        it simulates realistic telemetry.

        Args:
            deployment_id: Deployment to monitor.
            n_samples: Number of synthetic request samples to simulate.

        Returns:
            Current :class:`CanaryMetrics` snapshot.

        Raises:
            KeyError: If ``deployment_id`` is not found.
        """
        if deployment_id not in self.deployments:
            raise KeyError(f"Deployment '{deployment_id}' not found")

        await asyncio.sleep(0)
        rng = np.random.default_rng(seed=int(datetime.now(timezone.utc).timestamp()) % (2**16))

        latencies = rng.lognormal(mean=4.5, sigma=0.5, size=n_samples)  # ~ms
        errors = rng.binomial(1, 0.01, size=n_samples)

        metrics = CanaryMetrics(
            deployment_id=deployment_id,
            error_rate=round(float(errors.mean()), 4),
            p50_latency_ms=round(float(np.percentile(latencies, 50)), 2),
            p99_latency_ms=round(float(np.percentile(latencies, 99)), 2),
            requests_served=n_samples,
        )
        self._metrics_history[deployment_id].append(metrics)
        logger.debug(
            "Canary metrics: err={:.2%}, p50={:.1f}ms, p99={:.1f}ms",
            metrics.error_rate,
            metrics.p50_latency_ms,
            metrics.p99_latency_ms,
        )
        return metrics

    async def promote(self, deployment_id: str) -> bool:
        """Promote the canary to 100% traffic.

        Checks that recent metrics are within thresholds before promoting.

        Args:
            deployment_id: Deployment to promote.

        Returns:
            ``True`` if promotion succeeded, ``False`` if blocked by metrics.

        Raises:
            KeyError: If ``deployment_id`` is not found.
            RuntimeError: If the deployment is not in CANARY state.
        """
        config = self._get_deployment(deployment_id, expected_state=DeploymentState.CANARY)

        metrics = await self.monitor_metrics(deployment_id)
        if not self._metrics_healthy(metrics, config):
            logger.warning(
                "Promotion blocked for '{}': metrics unhealthy (err={:.2%}, p99={:.1f}ms)",
                deployment_id,
                metrics.error_rate,
                metrics.p99_latency_ms,
            )
            return False

        self._states[deployment_id] = DeploymentState.STABLE
        logger.info(
            "Canary '{}' promoted to stable (model='{}')",
            deployment_id,
            config.model_id,
        )
        return True

    async def rollback(self, deployment_id: str, reason: str = "manual") -> None:
        """Roll back the canary to the baseline model.

        Args:
            deployment_id: Deployment to roll back.
            reason: Human-readable rollback reason for audit logging.

        Raises:
            KeyError: If ``deployment_id`` is not found.
        """
        if deployment_id not in self.deployments:
            raise KeyError(f"Deployment '{deployment_id}' not found")

        config = self.deployments[deployment_id]
        self._states[deployment_id] = DeploymentState.ROLLED_BACK
        await asyncio.sleep(0)
        logger.warning(
            "Canary '{}' rolled back to '{}': {}",
            deployment_id,
            config.baseline_model_id,
            reason,
        )

    def get_state(self, deployment_id: str) -> DeploymentState:
        """Return the current state of a deployment.

        Args:
            deployment_id: Deployment identifier.

        Returns:
            Current :class:`DeploymentState`.

        Raises:
            KeyError: If ``deployment_id`` is not found.
        """
        if deployment_id not in self._states:
            raise KeyError(f"Deployment '{deployment_id}' not found")
        return self._states[deployment_id]

    def _metrics_healthy(self, metrics: CanaryMetrics, config: CanaryConfig) -> bool:
        """Check whether canary metrics satisfy health thresholds.

        Args:
            metrics: Current telemetry snapshot.
            config: Deployment configuration with threshold values.

        Returns:
            ``True`` if all thresholds are satisfied.
        """
        return (
            metrics.error_rate <= config.error_rate_threshold
            and metrics.p99_latency_ms <= config.latency_threshold_ms
        )

    def _get_deployment(
        self,
        deployment_id: str,
        expected_state: DeploymentState | None = None,
    ) -> CanaryConfig:
        """Retrieve a deployment, optionally asserting its state.

        Args:
            deployment_id: Deployment identifier.
            expected_state: If set, raises if current state differs.

        Returns:
            The :class:`CanaryConfig`.

        Raises:
            KeyError: If not found.
            RuntimeError: If state assertion fails.
        """
        if deployment_id not in self.deployments:
            raise KeyError(f"Deployment '{deployment_id}' not found")
        if expected_state is not None:
            current = self._states[deployment_id]
            if current != expected_state:
                raise RuntimeError(
                    f"Deployment '{deployment_id}' is in state {current.name}, "
                    f"expected {expected_state.name}"
                )
        return self.deployments[deployment_id]
