"""Meta-Cognitive module – self-awareness, reflection, and blind-spot detection.

The AGI uses this module to examine its own reasoning, calibrate confidence,
and surface areas where its knowledge or data coverage may be insufficient.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


@dataclass
class ReflectionResult:
    """Output of a single reflection pass.

    Attributes:
        observations: List of textual findings from the reflection.
        confidence_estimate: Revised overall confidence after reflection.
        blindspots: Identified areas with insufficient coverage or data.
        recommendations: Suggested actions to address weaknesses.
    """

    observations: list[str] = field(default_factory=list)
    confidence_estimate: float = 0.0
    blindspots: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class MetaCognitive:
    """Self-awareness and reflection module for the AGI orchestrator.

    Maintains a rolling history of reflection results and tracks known
    blind-spots to guide adaptive improvement.

    Attributes:
        _reflection_history: Ordered list of past :class:`ReflectionResult`.
        _known_blindspots: Accumulated set of known coverage gaps.
    """

    def __init__(self) -> None:
        """Initialise with empty reflection history and no known blind-spots."""
        self._reflection_history: list[ReflectionResult] = []
        self._known_blindspots: set[str] = set()
        log.info("MetaCognitive initialised")

    def reflect(self, context: dict[str, Any]) -> ReflectionResult:
        """Analyse the current context and produce a reflection result.

        Args:
            context: Ambient information dict provided by the orchestrator
                (e.g. recent decisions, signal coverage, error rates).

        Returns:
            A :class:`ReflectionResult` describing findings and recommendations.

        Raises:
            TypeError: If *context* is not a dict.
        """
        if not isinstance(context, dict):
            raise TypeError(f"context must be a dict, got {type(context).__name__}")

        observations: list[str] = []
        recommendations: list[str] = []

        # Inspect error rate signal.
        error_rate: float = float(context.get("error_rate", 0.0))
        if error_rate > 0.1:
            observations.append(f"High error rate detected: {error_rate:.2%}")
            recommendations.append("Investigate recent failures and review decision thresholds")

        # Inspect signal coverage.
        signal_sources: list[str] = context.get("signal_sources", [])
        if len(signal_sources) < 3:
            observations.append(f"Low signal diversity: {len(signal_sources)} source(s)")
            recommendations.append("Integrate additional signal providers to improve coverage")

        if not observations:
            observations.append("No critical issues detected in current context")

        confidence = self.assess_confidence(context)
        blindspots = self.detect_blindspots(context)

        result = ReflectionResult(
            observations=observations,
            confidence_estimate=confidence,
            blindspots=blindspots,
            recommendations=recommendations,
        )
        self._reflection_history.append(result)
        log.info(
            "Reflection complete",
            observations=len(observations),
            confidence=f"{confidence:.3f}",
            blindspots=blindspots,
        )
        return result

    def assess_confidence(self, context: dict[str, Any]) -> float:
        """Estimate the current confidence level from context signals.

        Args:
            context: Ambient information dict.

        Returns:
            Confidence score in ``[0.0, 1.0]``.
        """
        base_confidence = float(context.get("base_confidence", 0.7))
        error_rate = float(context.get("error_rate", 0.0))
        data_freshness = float(context.get("data_freshness", 1.0))

        # Penalise for error rate and stale data.
        adjusted = base_confidence * (1.0 - error_rate) * data_freshness
        confidence = max(0.0, min(1.0, adjusted))
        log.debug("Confidence assessed", confidence=f"{confidence:.3f}")
        return confidence

    def detect_blindspots(self, context: dict[str, Any]) -> list[str]:
        """Identify coverage gaps not addressed by the current context.

        Args:
            context: Ambient information dict.

        Returns:
            List of string descriptions of identified blind-spots.
        """
        blindspots: list[str] = []
        required_keys = {"market_regime", "liquidity", "volatility", "sentiment"}
        missing = required_keys - set(context.keys())

        for key in sorted(missing):
            blindspots.append(f"Missing context variable: '{key}'")
            self._known_blindspots.add(key)

        log.debug("Blindspots detected", count=len(blindspots))
        return blindspots

    def get_reflection_summary(self) -> dict[str, Any]:
        """Return an aggregate summary over all past reflection results.

        Returns:
            Dict with ``total_reflections``, ``mean_confidence``,
            ``all_blindspots``, and ``last_recommendations``.
        """
        if not self._reflection_history:
            return {
                "total_reflections": 0,
                "mean_confidence": 0.0,
                "all_blindspots": [],
                "last_recommendations": [],
            }

        mean_conf = sum(r.confidence_estimate for r in self._reflection_history) / len(
            self._reflection_history
        )
        last = self._reflection_history[-1]

        return {
            "total_reflections": len(self._reflection_history),
            "mean_confidence": mean_conf,
            "all_blindspots": sorted(self._known_blindspots),
            "last_recommendations": last.recommendations,
        }
