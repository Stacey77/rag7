"""Attention Mechanism – focus prioritisation for contextual input processing.

Computes attention scores over a set of named input items and returns a
ranked focus list so downstream models concentrate on the most salient signals.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")


@dataclass
class AttentionScore:
    """Attention weight assigned to a single context item.

    Attributes:
        key: Item identifier (e.g. ``"volatility"``, ``"momentum"``).
        raw_score: Unnormalised relevance score.
        attention_weight: Softmax-normalised weight in ``(0, 1)``.
    """

    key: str
    raw_score: float
    attention_weight: float = 0.0


@dataclass
class AttentionResult:
    """Output of an attention computation pass.

    Attributes:
        scores: All scored items with their normalised weights.
        focus_areas: Keys whose attention weight exceeds the focus threshold.
        query: The original query that drove the computation.
    """

    scores: list[AttentionScore] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    query: dict[str, Any] = field(default_factory=dict)


class AttentionMechanism:
    """Soft attention over named context items using scaled dot-product scoring.

    Attributes:
        _focus_threshold: Minimum normalised weight to qualify as a focus area.
        _temperature: Softmax temperature controlling distribution sharpness.
    """

    def __init__(
        self,
        focus_threshold: float = 0.1,
        temperature: float = 1.0,
    ) -> None:
        """Initialise the attention mechanism.

        Args:
            focus_threshold: Minimum softmax weight for a key to be listed as a
                focus area. Defaults to ``0.1``.
            temperature: Softmax temperature. Values < 1 sharpen the
                distribution; values > 1 flatten it. Defaults to ``1.0``.

        Raises:
            ValueError: If *temperature* ≤ 0.
        """
        if temperature <= 0:
            raise ValueError(f"temperature must be positive, got {temperature}")
        self._focus_threshold = focus_threshold
        self._temperature = temperature
        log.info(
            "AttentionMechanism initialised",
            focus_threshold=focus_threshold,
            temperature=temperature,
        )

    def compute_attention(
        self,
        context: dict[str, Any],
        query: dict[str, Any],
    ) -> AttentionResult:
        """Compute softmax attention weights over *context* items given *query*.

        The raw score for each context key is computed as the dot product
        between the query's ``weights`` dict and the numeric context value.
        Non-numeric values receive a score of ``0.0``.

        Args:
            context: Mapping of feature names to numeric values.
            query: Dict carrying an optional ``weights`` sub-dict mapping
                context keys to query-side importance scalars.

        Returns:
            :class:`AttentionResult` with per-item scores and focus areas.

        Raises:
            TypeError: If *context* or *query* is not a dict.
        """
        if not isinstance(context, dict):
            raise TypeError(f"context must be a dict, got {type(context).__name__}")
        if not isinstance(query, dict):
            raise TypeError(f"query must be a dict, got {type(query).__name__}")

        query_weights: dict[str, float] = {
            k: float(v) for k, v in query.get("weights", {}).items()
        }

        raw_scores: list[AttentionScore] = []
        for key, value in context.items():
            try:
                num_value = float(value)
            except (TypeError, ValueError):
                num_value = 0.0
            q_weight = query_weights.get(key, 1.0)
            raw_scores.append(AttentionScore(key=key, raw_score=num_value * q_weight))

        softmax_weights = self._softmax([s.raw_score for s in raw_scores])
        for score, weight in zip(raw_scores, softmax_weights):
            score.attention_weight = weight

        focus_areas = [
            s.key for s in raw_scores if s.attention_weight >= self._focus_threshold
        ]
        focus_areas.sort(key=lambda k: next(s.attention_weight for s in raw_scores if s.key == k), reverse=True)

        result = AttentionResult(scores=raw_scores, focus_areas=focus_areas, query=query)
        log.debug(
            "Attention computed",
            items=len(raw_scores),
            focus_areas=focus_areas,
        )
        return result

    def get_focus_areas(
        self,
        context: dict[str, Any],
        query: dict[str, Any],
        top_k: int | None = None,
    ) -> list[str]:
        """Convenience wrapper returning only the focus-area key list.

        Args:
            context: Mapping of feature names to numeric values.
            query: Query dict as described in :meth:`compute_attention`.
            top_k: If provided, limits the result to the *k* highest-weighted
                focus areas.

        Returns:
            List of focus-area key strings ordered by descending attention weight.
        """
        result = self.compute_attention(context, query)
        areas = result.focus_areas
        return areas[:top_k] if top_k is not None else areas

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _softmax(self, values: list[float]) -> list[float]:
        """Compute temperature-scaled softmax over *values*.

        Args:
            values: List of raw score floats.

        Returns:
            Normalised probability list summing to 1.0.
        """
        if not values:
            return []
        scaled = [v / self._temperature for v in values]
        max_v = max(scaled)
        exps = [math.exp(v - max_v) for v in scaled]
        total = sum(exps)
        return [e / total for e in exps]
