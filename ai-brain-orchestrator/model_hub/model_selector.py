"""Model Selector – dynamic model selection based on market conditions.

Evaluates registered models against current market context metrics and
selects the most appropriate candidate for inference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")


@dataclass
class SelectionCriteria:
    """Criteria used to evaluate and rank candidate models.

    Attributes:
        market_regime: Current regime label (e.g. ``"trending"``, ``"ranging"``).
        volatility: Normalised volatility level in ``[0.0, 1.0]``.
        required_tags: Model tags that must all be present for a model to qualify.
        min_metric: Minimum performance metric threshold keyed by metric name.
    """

    market_regime: str = "unknown"
    volatility: float = 0.5
    required_tags: list[str] = field(default_factory=list)
    min_metric: dict[str, float] = field(default_factory=dict)


@dataclass
class EvaluationRecord:
    """Historical performance record for a single model.

    Attributes:
        model_id: Registry identifier.
        metric_name: Name of the tracked metric.
        score: Measured metric value.
        regime: Market regime at evaluation time.
    """

    model_id: str
    metric_name: str
    score: float
    regime: str = "unknown"


class ModelSelector:
    """Dynamic model selection engine for context-aware inference routing.

    Attributes:
        registry: Optional :class:`ModelRegistry` for descriptor look-ups.
        _evaluations: Per-model evaluation history.
    """

    def __init__(self, registry: Any | None = None) -> None:
        """Initialise the selector with an optional registry reference.

        Args:
            registry: Optional :class:`ModelRegistry` instance.
        """
        self.registry = registry
        self._evaluations: dict[str, list[EvaluationRecord]] = {}
        log.info("ModelSelector initialised")

    def evaluate_performance(self, record: EvaluationRecord) -> None:
        """Record a performance observation for a model.

        Args:
            record: :class:`EvaluationRecord` to append to the model's history.
        """
        self._evaluations.setdefault(record.model_id, []).append(record)
        log.debug(
            "Performance recorded",
            model_id=record.model_id,
            metric=record.metric_name,
            score=record.score,
            regime=record.regime,
        )

    def select(
        self,
        criteria: SelectionCriteria,
        candidate_ids: list[str] | None = None,
    ) -> str | None:
        """Choose the best model given *criteria* from the available candidates.

        Ranking uses the mean score of evaluations that match the requested
        regime. When no regime-specific evaluations exist, all evaluations are
        used. Models failing ``min_metric`` constraints are excluded.

        Args:
            criteria: :class:`SelectionCriteria` describing the current context.
            candidate_ids: Explicit allow-list of model IDs to consider.  When
                *None*, all models with evaluation records are considered.

        Returns:
            The ``model_id`` of the best candidate, or *None* if none qualify.
        """
        pool = candidate_ids if candidate_ids is not None else list(self._evaluations.keys())

        # Apply tag filter when a registry is available.
        if self.registry and criteria.required_tags:
            filtered = []
            for mid in pool:
                try:
                    desc = self.registry.get(mid)
                    if all(t in desc.tags for t in criteria.required_tags):
                        filtered.append(mid)
                except KeyError:
                    pass
            pool = filtered

        scores: dict[str, float] = {}
        for mid in pool:
            history = self._evaluations.get(mid, [])
            if not history:
                continue

            # Prefer regime-matched records.
            regime_records = [e for e in history if e.regime == criteria.market_regime]
            relevant = regime_records if regime_records else history

            mean_score = sum(e.score for e in relevant) / len(relevant)

            # Enforce min_metric constraints.
            disqualified = False
            for metric, threshold in criteria.min_metric.items():
                metric_records = [e for e in relevant if e.metric_name == metric]
                if metric_records:
                    best = max(e.score for e in metric_records)
                    if best < threshold:
                        disqualified = True
                        break
            if not disqualified:
                scores[mid] = mean_score

        if not scores:
            log.warning("No qualifying models found", regime=criteria.market_regime)
            return None

        winner = max(scores, key=lambda m: scores[m])
        log.info(
            "Model selected",
            model_id=winner,
            score=f"{scores[winner]:.4f}",
            regime=criteria.market_regime,
        )
        return winner
