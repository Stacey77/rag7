"""A/B testing framework for model comparison with statistical significance."""

from __future__ import annotations

import asyncio
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class Experiment:
    """An A/B experiment comparing two model variants.

    Attributes:
        experiment_id: Unique identifier.
        name: Human-readable name.
        control_model_id: Identifier of the control (baseline) model.
        treatment_model_id: Identifier of the treatment (challenger) model.
        traffic_split: Fraction of traffic routed to treatment (0–1).
        created_at: UTC creation timestamp.
        active: Whether the experiment is currently running.
        min_samples: Minimum observations before analysis is valid.
    """

    experiment_id: str
    name: str
    control_model_id: str
    treatment_model_id: str
    traffic_split: float = 0.5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True
    min_samples: int = 100


@dataclass
class ExperimentResults:
    """Statistical analysis results for an A/B experiment.

    Attributes:
        experiment_id: Identifier of the analysed experiment.
        control_mean: Mean metric for the control group.
        treatment_mean: Mean metric for the treatment group.
        relative_lift: Relative improvement of treatment over control.
        p_value: Two-sided p-value from a Welch t-test.
        significant: Whether the result is statistically significant.
        confidence_level: Confidence level used (e.g. 0.95).
        n_control: Number of control observations.
        n_treatment: Number of treatment observations.
    """

    experiment_id: str
    control_mean: float
    treatment_mean: float
    relative_lift: float
    p_value: float
    significant: bool
    confidence_level: float
    n_control: int
    n_treatment: int


class ABTesting:
    """Model A/B testing with statistical significance analysis.

    Manages concurrent experiments, routes inference requests to the
    appropriate model variant, and performs Welch's t-test to determine
    significance.

    Attributes:
        experiments: Active and completed experiments keyed by ID.
        _observations: Metric observations per experiment/variant.
        _rng: Seeded random generator for reproducible routing.
    """

    def __init__(self, random_seed: int = 42) -> None:
        """Initialise the A/B testing framework.

        Args:
            random_seed: Seed for the routing random number generator.
        """
        self.experiments: dict[str, Experiment] = {}
        self._observations: dict[str, dict[str, list[float]]] = {}
        self._rng = np.random.default_rng(seed=random_seed)
        logger.info("ABTesting initialised")

    def create_experiment(
        self,
        name: str,
        control_model_id: str,
        treatment_model_id: str,
        traffic_split: float = 0.5,
        min_samples: int = 100,
    ) -> Experiment:
        """Create and register a new A/B experiment.

        Args:
            name: Human-readable experiment name.
            control_model_id: Model ID for the control variant.
            treatment_model_id: Model ID for the treatment variant.
            traffic_split: Fraction of traffic to treatment (0–1).
            min_samples: Minimum samples per arm before analysis.

        Returns:
            The newly created :class:`Experiment`.

        Raises:
            ValueError: If ``traffic_split`` is not in (0, 1).
            ValueError: If ``control_model_id == treatment_model_id``.
        """
        if not 0 < traffic_split < 1:
            raise ValueError(f"traffic_split must be in (0, 1), got {traffic_split}")
        if control_model_id == treatment_model_id:
            raise ValueError("control and treatment models must differ")

        experiment_id = str(uuid.uuid4())
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            control_model_id=control_model_id,
            treatment_model_id=treatment_model_id,
            traffic_split=traffic_split,
            min_samples=min_samples,
        )
        self.experiments[experiment_id] = experiment
        self._observations[experiment_id] = {"control": [], "treatment": []}
        logger.info(
            "Experiment '{}' created (id={}, split={:.0%} treatment)",
            name,
            experiment_id,
            traffic_split,
        )
        return experiment

    def route_request(self, experiment_id: str) -> tuple[str, str]:
        """Determine which model variant should serve a request.

        Args:
            experiment_id: Identifier of the experiment.

        Returns:
            Tuple of ``(variant, model_id)`` where variant is either
            ``"control"`` or ``"treatment"``.

        Raises:
            KeyError: If ``experiment_id`` is not found.
            RuntimeError: If the experiment is no longer active.
        """
        experiment = self._get_active_experiment(experiment_id)
        variant = (
            "treatment"
            if self._rng.random() < experiment.traffic_split
            else "control"
        )
        model_id = (
            experiment.treatment_model_id
            if variant == "treatment"
            else experiment.control_model_id
        )
        logger.debug("Routing request to {} ({})", variant, model_id)
        return variant, model_id

    def record_observation(
        self,
        experiment_id: str,
        variant: str,
        metric_value: float,
    ) -> None:
        """Record a metric observation for a variant.

        Args:
            experiment_id: Experiment identifier.
            variant: ``"control"`` or ``"treatment"``.
            metric_value: Observed metric value (e.g. latency, accuracy).

        Raises:
            KeyError: If ``experiment_id`` is not found.
            ValueError: If ``variant`` is not ``"control"`` or ``"treatment"``.
        """
        if experiment_id not in self._observations:
            raise KeyError(f"Experiment '{experiment_id}' not found")
        if variant not in ("control", "treatment"):
            raise ValueError(f"variant must be 'control' or 'treatment', got '{variant}'")
        self._observations[experiment_id][variant].append(metric_value)

    def analyze_results(
        self,
        experiment_id: str,
        confidence_level: float = 0.95,
    ) -> ExperimentResults:
        """Analyse experiment results using Welch's t-test.

        Args:
            experiment_id: Experiment to analyse.
            confidence_level: Statistical significance threshold (e.g. 0.95).

        Returns:
            :class:`ExperimentResults` with significance and lift metrics.

        Raises:
            KeyError: If ``experiment_id`` is not found.
            ValueError: If either arm has fewer observations than
                ``experiment.min_samples``.
        """
        if experiment_id not in self.experiments:
            raise KeyError(f"Experiment '{experiment_id}' not found")

        experiment = self.experiments[experiment_id]
        obs = self._observations[experiment_id]
        ctrl = np.asarray(obs["control"], dtype=float)
        trt = np.asarray(obs["treatment"], dtype=float)

        if len(ctrl) < experiment.min_samples or len(trt) < experiment.min_samples:
            raise ValueError(
                f"Insufficient data: control={len(ctrl)}, treatment={len(trt)}, "
                f"need {experiment.min_samples} each"
            )

        ctrl_mean = float(np.mean(ctrl))
        trt_mean = float(np.mean(trt))
        relative_lift = (trt_mean - ctrl_mean) / (ctrl_mean + 1e-10)

        p_value = self._welch_t_test(ctrl, trt)
        alpha = 1.0 - confidence_level
        significant = p_value < alpha

        result = ExperimentResults(
            experiment_id=experiment_id,
            control_mean=round(ctrl_mean, 6),
            treatment_mean=round(trt_mean, 6),
            relative_lift=round(relative_lift, 4),
            p_value=round(p_value, 6),
            significant=significant,
            confidence_level=confidence_level,
            n_control=len(ctrl),
            n_treatment=len(trt),
        )
        logger.info(
            "Experiment '{}' analysis: lift={:.2%}, p={:.4f}, significant={}",
            experiment.name,
            relative_lift,
            p_value,
            significant,
        )
        return result

    def _welch_t_test(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute a two-sided Welch's t-test p-value.

        Args:
            a: Observations for group A.
            b: Observations for group B.

        Returns:
            Two-sided p-value.
        """
        n_a, n_b = len(a), len(b)
        mean_a, mean_b = np.mean(a), np.mean(b)
        var_a = np.var(a, ddof=1) if n_a > 1 else 0.0
        var_b = np.var(b, ddof=1) if n_b > 1 else 0.0

        se = math.sqrt(var_a / n_a + var_b / n_b + 1e-12)
        t_stat = (mean_a - mean_b) / se

        # Welch–Satterthwaite degrees of freedom
        num = (var_a / n_a + var_b / n_b) ** 2
        denom = (var_a / n_a) ** 2 / (n_a - 1 + 1e-12) + (var_b / n_b) ** 2 / (n_b - 1 + 1e-12)
        df = num / (denom + 1e-12)

        # Approximate p-value using normal distribution for large df
        z = abs(t_stat)
        p_value = 2 * (1 - self._normal_cdf(z))
        return float(np.clip(p_value, 0.0, 1.0))

    @staticmethod
    def _normal_cdf(z: float) -> float:
        """Standard normal CDF via the error function.

        Args:
            z: Z-score.

        Returns:
            Probability P(Z ≤ z).
        """
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    def _get_active_experiment(self, experiment_id: str) -> Experiment:
        """Fetch an active experiment by ID.

        Args:
            experiment_id: Experiment identifier.

        Returns:
            The :class:`Experiment` object.

        Raises:
            KeyError: If not found.
            RuntimeError: If inactive.
        """
        if experiment_id not in self.experiments:
            raise KeyError(f"Experiment '{experiment_id}' not found")
        experiment = self.experiments[experiment_id]
        if not experiment.active:
            raise RuntimeError(f"Experiment '{experiment_id}' is no longer active")
        return experiment

    async def async_route_request(self, experiment_id: str) -> tuple[str, str]:
        """Async wrapper around :meth:`route_request` for use in async pipelines.

        Args:
            experiment_id: Identifier of the experiment.

        Returns:
            Tuple of ``(variant, model_id)``.
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self.route_request, experiment_id
        )

    async def async_analyze_results(
        self,
        experiment_id: str,
        confidence_level: float = 0.95,
    ) -> ExperimentResults:
        """Async wrapper around :meth:`analyze_results` for use in async pipelines.

        Args:
            experiment_id: Experiment to analyse.
            confidence_level: Statistical significance threshold.

        Returns:
            :class:`ExperimentResults` with significance and lift metrics.
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self.analyze_results, experiment_id, confidence_level
        )

    def stop_experiment(self, experiment_id: str) -> None:
        """Mark an experiment as inactive.

        Args:
            experiment_id: Experiment to stop.

        Raises:
            KeyError: If not found.
        """
        if experiment_id not in self.experiments:
            raise KeyError(f"Experiment '{experiment_id}' not found")
        self.experiments[experiment_id].active = False
        logger.info("Experiment '{}' stopped", experiment_id)
