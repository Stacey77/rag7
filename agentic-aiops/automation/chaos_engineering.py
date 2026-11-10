"""Chaos engineering framework for resilience testing via controlled failure injection."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Awaitable

import numpy as np
from loguru import logger


class ExperimentType(Enum):
    """Categories of chaos experiment."""

    LATENCY_INJECTION = auto()
    ERROR_INJECTION = auto()
    CPU_STRESS = auto()
    MEMORY_STRESS = auto()
    NETWORK_PARTITION = auto()
    PROCESS_KILL = auto()
    DISK_FILL = auto()


class ExperimentStatus(Enum):
    """Lifecycle states of a chaos experiment."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    ABORTED = auto()
    FAILED = auto()


@dataclass
class ChaosExperiment:
    """Specification for a chaos engineering experiment.

    Attributes:
        experiment_id: Unique identifier.
        name: Human-readable name.
        experiment_type: Category of failure to inject.
        target_component: Service or component under test.
        blast_radius: Fraction of traffic/instances affected (0–1).
        duration_seconds: How long to sustain the failure.
        parameters: Type-specific parameters (e.g. latency_ms, error_rate).
        hypothesis: Expected system behaviour under this failure.
        abort_conditions: Metric conditions that trigger experiment abort.
    """

    experiment_id: str
    name: str
    experiment_type: ExperimentType
    target_component: str
    blast_radius: float
    duration_seconds: float
    parameters: dict[str, Any] = field(default_factory=dict)
    hypothesis: str = ""
    abort_conditions: dict[str, float] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Outcome of a chaos experiment.

    Attributes:
        experiment_id: Owning experiment identifier.
        status: Final experiment status.
        hypothesis_validated: Whether the hypothesis held under failure.
        observations: Key metric observations during the experiment.
        abort_reason: Reason for abort if status is ABORTED.
        started_at: UTC start timestamp.
        completed_at: UTC completion timestamp.
        duration_ms: Actual experiment duration.
    """

    experiment_id: str
    status: ExperimentStatus
    hypothesis_validated: bool
    observations: dict[str, Any]
    abort_reason: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    duration_ms: float = 0.0


class ChaosEngineering:
    """Resilience testing framework with controlled failure injection.

    Implements the chaos engineering principles: define steady state,
    hypothesise, inject failure, observe, validate.

    Attributes:
        experiments: Registered experiments keyed by ID.
        results: Completed experiment results.
        _abort_callbacks: Optional callbacks invoked on abort conditions.
        _steady_state_metrics: Baseline metrics for comparison.
    """

    def __init__(self) -> None:
        """Initialise the chaos engineering framework."""
        self.experiments: dict[str, ChaosExperiment] = {}
        self.results: list[ExperimentResult] = []
        self._steady_state_metrics: dict[str, float] = {}
        logger.info("ChaosEngineering framework initialised")

    def define_steady_state(self, metrics: dict[str, float]) -> None:
        """Define the system steady state for hypothesis validation.

        Args:
            metrics: Mapping of metric name to acceptable baseline value.
        """
        self._steady_state_metrics = dict(metrics)
        logger.info("Steady state defined: {}", metrics)

    def create_experiment(
        self,
        name: str,
        experiment_type: ExperimentType,
        target_component: str,
        blast_radius: float = 0.1,
        duration_seconds: float = 60.0,
        parameters: dict[str, Any] | None = None,
        hypothesis: str = "",
        abort_conditions: dict[str, float] | None = None,
    ) -> ChaosExperiment:
        """Create and register a chaos experiment.

        Args:
            name: Experiment name.
            experiment_type: Type of failure to inject.
            target_component: Target service.
            blast_radius: Fraction of instances/traffic affected (0–1).
            duration_seconds: Experiment duration.
            parameters: Type-specific parameters.
            hypothesis: Expected behaviour description.
            abort_conditions: Metric thresholds that trigger abort.

        Returns:
            The created :class:`ChaosExperiment`.

        Raises:
            ValueError: If ``blast_radius`` is not in (0, 1].
        """
        if not 0 < blast_radius <= 1.0:
            raise ValueError(f"blast_radius must be in (0, 1], got {blast_radius}")

        experiment_id = str(uuid.uuid4())
        experiment = ChaosExperiment(
            experiment_id=experiment_id,
            name=name,
            experiment_type=experiment_type,
            target_component=target_component,
            blast_radius=blast_radius,
            duration_seconds=duration_seconds,
            parameters=parameters or {},
            hypothesis=hypothesis,
            abort_conditions=abort_conditions or {},
        )
        self.experiments[experiment_id] = experiment
        logger.info(
            "Chaos experiment '{}' created (id={}, type={}, radius={:.0%})",
            name,
            experiment_id,
            experiment_type.name,
            blast_radius,
        )
        return experiment

    async def run_experiment(
        self,
        experiment_id: str,
        metric_collector: Callable[[], Awaitable[dict[str, float]]] | None = None,
    ) -> ExperimentResult:
        """Execute a chaos experiment with monitoring and auto-abort.

        Args:
            experiment_id: Experiment to run.
            metric_collector: Async callable returning live metrics during
                the experiment.  Uses a simulator when ``None``.

        Returns:
            :class:`ExperimentResult` with observations and outcome.

        Raises:
            KeyError: If ``experiment_id`` is not found.
        """
        experiment = self._get_experiment(experiment_id)
        import time
        start_ts = datetime.now(timezone.utc)
        start_mono = time.monotonic()

        logger.warning(
            "CHAOS: Starting '{}' on '{}' ({:.0%} blast radius, {}s)",
            experiment.name,
            experiment.target_component,
            experiment.blast_radius,
            experiment.duration_seconds,
        )

        observations: dict[str, Any] = {
            "experiment_type": experiment.experiment_type.name,
            "target": experiment.target_component,
            "blast_radius": experiment.blast_radius,
            "metric_samples": [],
        }
        status = ExperimentStatus.COMPLETED
        abort_reason = ""

        try:
            await self._inject_failure(experiment)
            collector = metric_collector or self._default_metric_collector
            n_samples = max(3, int(experiment.duration_seconds / 10))

            for _ in range(n_samples):
                await asyncio.sleep(0)
                live_metrics = await collector()
                observations["metric_samples"].append(live_metrics)

                # Check abort conditions
                abort_triggered, abort_reason = self._check_abort(
                    live_metrics, experiment.abort_conditions
                )
                if abort_triggered:
                    status = ExperimentStatus.ABORTED
                    logger.error("Experiment aborted: {}", abort_reason)
                    break

            await self._remove_failure(experiment)

        except Exception as exc:
            status = ExperimentStatus.FAILED
            abort_reason = str(exc)
            logger.exception("Chaos experiment '{}' failed: {}", experiment_id, exc)

        duration_ms = (time.monotonic() - start_mono) * 1000
        hypothesis_validated = status == ExperimentStatus.COMPLETED and self._validate_hypothesis(
            observations
        )

        result = ExperimentResult(
            experiment_id=experiment_id,
            status=status,
            hypothesis_validated=hypothesis_validated,
            observations=observations,
            abort_reason=abort_reason,
            started_at=start_ts,
            completed_at=datetime.now(timezone.utc),
            duration_ms=round(duration_ms, 2),
        )
        self.results.append(result)
        logger.info(
            "Chaos experiment '{}' completed: status={}, hypothesis_validated={}",
            experiment_id,
            status.name,
            hypothesis_validated,
        )
        return result

    async def _inject_failure(self, experiment: ChaosExperiment) -> None:
        """Simulate failure injection for an experiment type.

        Args:
            experiment: Experiment specification.
        """
        await asyncio.sleep(0)
        logger.debug(
            "Injecting {} into '{}'", experiment.experiment_type.name, experiment.target_component
        )

    async def _remove_failure(self, experiment: ChaosExperiment) -> None:
        """Simulate failure removal (restore steady state).

        Args:
            experiment: Experiment specification.
        """
        await asyncio.sleep(0)
        logger.debug(
            "Removing {} from '{}'", experiment.experiment_type.name, experiment.target_component
        )

    async def _default_metric_collector(self) -> dict[str, float]:
        """Collect simulated metrics during an experiment.

        Returns:
            Dictionary of simulated metric readings.
        """
        await asyncio.sleep(0)
        rng = np.random.default_rng()
        return {
            "error_rate": float(rng.beta(2, 20)),
            "latency_p99_ms": float(rng.lognormal(5.0, 0.8)),
            "cpu_percent": float(rng.uniform(40, 90)),
            "availability": float(rng.uniform(0.95, 1.0)),
        }

    def _check_abort(
        self,
        metrics: dict[str, float],
        abort_conditions: dict[str, float],
    ) -> tuple[bool, str]:
        """Check whether any abort condition is breached.

        Args:
            metrics: Current metric readings.
            abort_conditions: Threshold mapping (abort if metric > threshold).

        Returns:
            Tuple of ``(should_abort, reason)``.
        """
        for metric, threshold in abort_conditions.items():
            value = metrics.get(metric)
            if value is not None and value > threshold:
                return True, f"{metric}={value:.4f} > abort threshold {threshold}"
        return False, ""

    def _validate_hypothesis(self, observations: dict[str, Any]) -> bool:
        """Validate the experiment hypothesis against steady state.

        Args:
            observations: Collected observations.

        Returns:
            ``True`` if steady state was maintained (hypothesis validated).
        """
        if not self._steady_state_metrics or not observations.get("metric_samples"):
            return True  # Cannot disprove

        samples = observations["metric_samples"]
        for metric, baseline in self._steady_state_metrics.items():
            values = [s.get(metric) for s in samples if metric in s]
            if not values:
                continue
            mean_value = float(np.mean(values))
            # Fail if mean deviates more than 50% from baseline
            if abs(mean_value - baseline) / (abs(baseline) + 1e-10) > 0.5:
                return False
        return True

    def _get_experiment(self, experiment_id: str) -> ChaosExperiment:
        """Retrieve an experiment by ID.

        Args:
            experiment_id: Experiment identifier.

        Returns:
            The :class:`ChaosExperiment`.

        Raises:
            KeyError: If not found.
        """
        if experiment_id not in self.experiments:
            raise KeyError(f"Experiment '{experiment_id}' not found")
        return self.experiments[experiment_id]
