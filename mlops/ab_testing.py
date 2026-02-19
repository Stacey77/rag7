"""Model A/B testing framework."""
from __future__ import annotations

import hashlib
import logging
import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Variant:
    name: str
    model_name: str
    model_version: str
    traffic_weight: float = 0.5    # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Experiment:
    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    variants: List[Variant] = field(default_factory=list)
    status: str = "draft"      # draft | running | paused | completed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    success_metric: str = "accuracy"
    minimum_samples: int = 100
    significance_level: float = 0.05
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Observation:
    experiment_id: str
    variant_name: str
    entity_id: str
    outcome: float       # e.g. 1.0 for success, 0.0 for failure
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VariantStats:
    variant_name: str
    sample_count: int = 0
    mean_outcome: float = 0.0
    std_outcome: float = 0.0
    conversion_rate: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)


@dataclass
class ExperimentResult:
    experiment_id: str = ""
    status: str = ""
    variant_stats: List[VariantStats] = field(default_factory=list)
    winner: Optional[str] = None
    p_value: float = 1.0
    is_significant: bool = False
    recommendation: str = ""
    computed_at: datetime = field(default_factory=datetime.utcnow)


def _welch_t_statistic(a: List[float], b: List[float]) -> Tuple[float, float]:
    """Compute approximate Welch t-test p-value (2-sided)."""
    import math
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
    mean_a, mean_b = statistics.mean(a), statistics.mean(b)
    var_a = statistics.variance(a)
    var_b = statistics.variance(b)
    se = math.sqrt(var_a / len(a) + var_b / len(b))
    if se == 0:
        return 0.0, 1.0
    t = (mean_a - mean_b) / se
    # Approximate p-value using normal distribution (z-test for large samples)
    from math import erfc, sqrt
    p_value = erfc(abs(t) / sqrt(2))
    return t, p_value


def _confidence_interval_95(values: List[float]) -> Tuple[float, float]:
    """95% confidence interval using t-distribution approximation."""
    import math
    if len(values) < 2:
        m = values[0] if values else 0.0
        return m, m
    mean = statistics.mean(values)
    se = statistics.stdev(values) / math.sqrt(len(values))
    margin = 1.96 * se
    return mean - margin, mean + margin


class TrafficSplitter:
    """Deterministic traffic routing by entity ID hashing."""

    def assign_variant(self, entity_id: str, variants: List[Variant]) -> Variant:
        """Deterministically route entity to a variant based on hash."""
        h = int(hashlib.md5(entity_id.encode()).hexdigest(), 16) % 1000 / 1000.0
        cumulative = 0.0
        total_weight = sum(v.traffic_weight for v in variants)
        for variant in variants:
            cumulative += variant.traffic_weight / total_weight
            if h < cumulative:
                return variant
        return variants[-1]


class ABTesting:
    """
    A/B testing framework for comparing ML models with statistical
    significance testing, traffic splitting, and experiment lifecycle management.
    """

    def __init__(self) -> None:
        self._experiments: Dict[str, Experiment] = {}
        self._observations: Dict[str, List[Observation]] = {}  # experiment_id -> observations
        self._splitter = TrafficSplitter()
        logger.info("ABTesting framework initialized")

    def create_experiment(self, name: str, control: Variant, treatment: Variant,
                           description: str = "",
                           success_metric: str = "accuracy",
                           minimum_samples: int = 100) -> Experiment:
        exp = Experiment(
            name=name,
            description=description,
            variants=[control, treatment],
            success_metric=success_metric,
            minimum_samples=minimum_samples,
        )
        # Normalize weights
        total = sum(v.traffic_weight for v in exp.variants)
        for v in exp.variants:
            v.traffic_weight = v.traffic_weight / total
        self._experiments[exp.experiment_id] = exp
        self._observations[exp.experiment_id] = []
        logger.info("Created experiment '%s' (%s)", name, exp.experiment_id)
        return exp

    def start(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status not in ("draft", "paused"):
            return False
        exp.status = "running"
        exp.start_time = datetime.utcnow()
        logger.info("Started experiment '%s'", exp.name)
        return True

    def pause(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != "running":
            return False
        exp.status = "paused"
        return True

    def route(self, experiment_id: str, entity_id: str) -> Optional[Variant]:
        """Route an entity to a variant for an active experiment."""
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != "running":
            return None
        return self._splitter.assign_variant(entity_id, exp.variants)

    def record_outcome(self, experiment_id: str, entity_id: str,
                        variant_name: str, outcome: float,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        obs = Observation(experiment_id=experiment_id, variant_name=variant_name,
                          entity_id=entity_id, outcome=outcome, metadata=metadata or {})
        self._observations.setdefault(experiment_id, []).append(obs)

    def analyze(self, experiment_id: str) -> ExperimentResult:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return ExperimentResult(experiment_id=experiment_id, status="not_found")

        observations = self._observations.get(experiment_id, [])
        variant_outcomes: Dict[str, List[float]] = {v.name: [] for v in exp.variants}
        for obs in observations:
            if obs.variant_name in variant_outcomes:
                variant_outcomes[obs.variant_name].append(obs.outcome)

        variant_stats: List[VariantStats] = []
        for variant_name, outcomes in variant_outcomes.items():
            if not outcomes:
                variant_stats.append(VariantStats(variant_name=variant_name))
                continue
            mean = statistics.mean(outcomes)
            std = statistics.stdev(outcomes) if len(outcomes) > 1 else 0.0
            ci = _confidence_interval_95(outcomes)
            variant_stats.append(VariantStats(
                variant_name=variant_name,
                sample_count=len(outcomes),
                mean_outcome=mean,
                std_outcome=std,
                conversion_rate=sum(1 for o in outcomes if o > 0.5) / len(outcomes),
                confidence_interval=ci,
            ))

        # Statistical significance test
        p_value = 1.0
        winner = None
        is_significant = False

        if len(exp.variants) >= 2:
            v1_outcomes = variant_outcomes.get(exp.variants[0].name, [])
            v2_outcomes = variant_outcomes.get(exp.variants[1].name, [])
            min_samples = exp.minimum_samples

            if len(v1_outcomes) >= min_samples and len(v2_outcomes) >= min_samples:
                _, p_value = _welch_t_statistic(v1_outcomes, v2_outcomes)
                is_significant = p_value < exp.significance_level
                if is_significant:
                    means = {v.variant_name: v.mean_outcome for v in variant_stats}
                    winner = max(means, key=lambda n: means[n])

        n_total = sum(len(o) for o in variant_outcomes.values())
        if n_total < exp.minimum_samples:
            recommendation = f"Collect more data (have {n_total}, need {exp.minimum_samples})."
        elif is_significant and winner:
            recommendation = f"Promote '{winner}' — statistically significant improvement (p={p_value:.4f})."
        else:
            recommendation = f"No significant difference detected (p={p_value:.4f}). Continue collecting."

        return ExperimentResult(
            experiment_id=experiment_id,
            status=exp.status,
            variant_stats=variant_stats,
            winner=winner,
            p_value=p_value,
            is_significant=is_significant,
            recommendation=recommendation,
        )

    def list_experiments(self, status: Optional[str] = None) -> List[Experiment]:
        if status:
            return [e for e in self._experiments.values() if e.status == status]
        return list(self._experiments.values())

    def complete(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return False
        exp.status = "completed"
        exp.end_time = datetime.utcnow()
        return True
