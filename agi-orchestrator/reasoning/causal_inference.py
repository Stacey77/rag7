"""Causal Inference Engine – do-calculus inspired causal reasoning.

Provides an abstract causal graph over market variables and estimates the
effect of one variable on another via lightweight structural equations, without
requiring a heavy ML framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


@dataclass
class CausalEdge:
    """A directed causal relationship between two variables.

    Attributes:
        cause: Name of the causing variable.
        effect: Name of the affected variable.
        strength: Estimated effect magnitude in ``[-1.0, 1.0]``.
        confidence: Confidence in the edge estimate, in ``[0.0, 1.0]``.
    """

    cause: str
    effect: str
    strength: float = 0.0
    confidence: float = 0.0


@dataclass
class CausalGraph:
    """Lightweight directed acyclic causal graph.

    Attributes:
        nodes: Set of variable names in the graph.
        edges: Mapping of ``(cause, effect)`` tuples to :class:`CausalEdge`.
    """

    nodes: set[str] = field(default_factory=set)
    edges: dict[tuple[str, str], CausalEdge] = field(default_factory=dict)

    def add_edge(self, edge: CausalEdge) -> None:
        """Insert or replace an edge in the graph.

        Args:
            edge: The :class:`CausalEdge` to add.
        """
        self.nodes.add(edge.cause)
        self.nodes.add(edge.effect)
        self.edges[(edge.cause, edge.effect)] = edge

    def get_causes(self, variable: str) -> list[CausalEdge]:
        """Return all edges whose effect is *variable*.

        Args:
            variable: Target variable name.

        Returns:
            List of :class:`CausalEdge` objects pointing to *variable*.
        """
        return [e for (_, eff), e in self.edges.items() if eff == variable]


class CausalInferenceEngine:
    """Causal reasoning engine supporting graph construction and effect estimation.

    Attributes:
        _graph: The maintained :class:`CausalGraph`.
    """

    def __init__(self) -> None:
        """Initialise with an empty causal graph."""
        self._graph: CausalGraph = CausalGraph()
        log.info("CausalInferenceEngine initialised")

    def build_causal_graph(self, observations: list[dict[str, Any]]) -> CausalGraph:
        """Construct or update the causal graph from a batch of observations.

        Each observation should be a dict mapping variable names to numeric
        values. Simple correlation heuristics are used to seed edge strengths.

        Args:
            observations: List of variable-value snapshots.

        Returns:
            The updated :class:`CausalGraph`.

        Raises:
            ValueError: If *observations* is empty.
        """
        if not observations:
            raise ValueError("observations must be non-empty")

        variables = list(observations[0].keys())

        for i, cause in enumerate(variables):
            for effect in variables[i + 1 :]:
                cause_vals = [o.get(cause, 0.0) for o in observations]
                effect_vals = [o.get(effect, 0.0) for o in observations]
                strength = self._pearson_corr(cause_vals, effect_vals)
                edge = CausalEdge(
                    cause=cause,
                    effect=effect,
                    strength=strength,
                    confidence=min(abs(strength), 1.0),
                )
                self._graph.add_edge(edge)

        log.info(
            "Causal graph built",
            nodes=len(self._graph.nodes),
            edges=len(self._graph.edges),
        )
        return self._graph

    def infer_causality(
        self, cause: str, effect: str
    ) -> dict[str, Any]:
        """Report whether a direct causal link exists from *cause* to *effect*.

        Args:
            cause: Name of the potential cause variable.
            effect: Name of the potential effect variable.

        Returns:
            Dict with ``cause``, ``effect``, ``strength``, ``confidence``, and
            ``causal`` (bool) indicating whether the link is considered strong.
        """
        edge = self._graph.edges.get((cause, effect))
        if edge is None:
            log.debug("No causal edge found", cause=cause, effect=effect)
            return {"cause": cause, "effect": effect, "strength": 0.0, "confidence": 0.0, "causal": False}

        result = {
            "cause": cause,
            "effect": effect,
            "strength": edge.strength,
            "confidence": edge.confidence,
            "causal": edge.confidence >= 0.5,
        }
        log.debug("Causality inferred", **result)
        return result

    def estimate_effect(
        self,
        cause: str,
        effect: str,
        intervention_value: float,
    ) -> float:
        """Estimate the change in *effect* given an intervention on *cause*.

        Uses the linear structural equation implied by the edge strength.

        Args:
            cause: The variable being intervened upon.
            effect: The downstream variable of interest.
            intervention_value: The do-calculus intervention value ``do(X=v)``.

        Returns:
            Estimated change in the effect variable.
        """
        edge = self._graph.edges.get((cause, effect))
        if edge is None:
            log.debug("No edge for effect estimation", cause=cause, effect=effect)
            return 0.0

        estimated = edge.strength * intervention_value
        log.debug(
            "Effect estimated",
            cause=cause,
            effect=effect,
            intervention=intervention_value,
            estimated_effect=estimated,
        )
        return estimated

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pearson_corr(x: list[float], y: list[float]) -> float:
        """Compute the Pearson correlation coefficient between *x* and *y*.

        Args:
            x: First numeric sequence.
            y: Second numeric sequence of equal length.

        Returns:
            Correlation in ``[-1.0, 1.0]``, or ``0.0`` when degenerate.
        """
        n = len(x)
        if n < 2:
            return 0.0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)
        denom = (var_x * var_y) ** 0.5
        return cov / denom if denom else 0.0
