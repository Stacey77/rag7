"""Self-Improvement – autonomous learning loops for strategy refinement.

Records trade/decision outcomes, analyses performance statistics, and proposes
strategy weight adjustments so that the AGI continuously improves over time.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


@dataclass
class Outcome:
    """A recorded decision outcome used for learning.

    Attributes:
        decision_id: Opaque identifier linking to the original decision.
        action: The action that was taken (e.g. ``"buy"``, ``"hold"``).
        predicted_confidence: Confidence at decision time.
        actual_return: Realised return (positive = profit).
        metadata: Arbitrary supporting data.
    """

    decision_id: str
    action: str
    predicted_confidence: float
    actual_return: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Summary statistics over a set of recorded outcomes.

    Attributes:
        sample_count: Number of outcomes analysed.
        mean_return: Average realised return.
        std_return: Standard deviation of returns (0.0 when < 2 samples).
        win_rate: Fraction of outcomes with positive return.
        mean_confidence_error: Average |predicted_confidence - win_indicator|.
        suggested_adjustments: Recommended strategy parameter updates.
    """

    sample_count: int
    mean_return: float
    std_return: float
    win_rate: float
    mean_confidence_error: float
    suggested_adjustments: dict[str, Any] = field(default_factory=dict)


class SelfImprovement:
    """Autonomous learning loop that refines strategy weights from outcomes.

    Attributes:
        _outcomes: Historical record of all submitted outcomes.
        _strategy_params: Mutable strategy parameters adjusted over time.
    """

    def __init__(self) -> None:
        """Initialise with an empty outcome history and default strategy params."""
        self._outcomes: list[Outcome] = []
        self._strategy_params: dict[str, float] = {
            "risk_tolerance": 0.5,
            "confidence_threshold": 0.6,
            "learning_rate": 0.01,
        }
        log.info("SelfImprovement initialised")

    def record_outcome(self, outcome: Outcome) -> None:
        """Append a new outcome to the history for future analysis.

        Args:
            outcome: The :class:`Outcome` instance to record.

        Raises:
            TypeError: If *outcome* is not an :class:`Outcome`.
        """
        if not isinstance(outcome, Outcome):
            raise TypeError(f"Expected Outcome, got {type(outcome).__name__}")
        self._outcomes.append(outcome)
        log.debug(
            "Outcome recorded",
            decision_id=outcome.decision_id,
            action=outcome.action,
            actual_return=outcome.actual_return,
        )

    def analyze_performance(self, window: int | None = None) -> PerformanceReport:
        """Compute descriptive statistics over the most recent *window* outcomes.

        Args:
            window: How many of the most recent outcomes to include. Uses all
                available outcomes when *None*.

        Returns:
            A :class:`PerformanceReport` summarising the analysed window.

        Raises:
            ValueError: If there are no recorded outcomes.
        """
        if not self._outcomes:
            raise ValueError("No outcomes recorded yet")

        sample = self._outcomes[-window:] if window else self._outcomes
        returns = [o.actual_return for o in sample]
        wins = [r for r in returns if r > 0]

        mean_ret = statistics.mean(returns)
        std_ret = statistics.stdev(returns) if len(returns) >= 2 else 0.0
        win_rate = len(wins) / len(returns)

        conf_errors = [
            abs(o.predicted_confidence - (1.0 if o.actual_return > 0 else 0.0))
            for o in sample
        ]
        mean_conf_err = statistics.mean(conf_errors)

        report = PerformanceReport(
            sample_count=len(sample),
            mean_return=mean_ret,
            std_return=std_ret,
            win_rate=win_rate,
            mean_confidence_error=mean_conf_err,
        )
        log.info(
            "Performance analysed",
            sample_count=report.sample_count,
            mean_return=f"{mean_ret:.4f}",
            win_rate=f"{win_rate:.2%}",
        )
        return report

    def update_strategy(self, report: PerformanceReport | None = None) -> dict[str, float]:
        """Adjust strategy parameters based on the latest performance report.

        When *report* is *None* a fresh :meth:`analyze_performance` call is
        made automatically.

        Args:
            report: Pre-computed :class:`PerformanceReport`. If *None*, one is
                generated from the full outcome history.

        Returns:
            The updated strategy parameters dictionary.

        Raises:
            ValueError: If there are no outcomes and *report* is *None*.
        """
        if report is None:
            report = self.analyze_performance()

        lr = self._strategy_params["learning_rate"]

        # Nudge risk tolerance toward win-rate signal.
        self._strategy_params["risk_tolerance"] += lr * (report.win_rate - 0.5)
        self._strategy_params["risk_tolerance"] = max(
            0.1, min(0.9, self._strategy_params["risk_tolerance"])
        )

        # Tighten confidence threshold when calibration error is large.
        if report.mean_confidence_error > 0.3:
            self._strategy_params["confidence_threshold"] = min(
                0.9, self._strategy_params["confidence_threshold"] + lr
            )

        report.suggested_adjustments = dict(self._strategy_params)
        log.info("Strategy updated", params=self._strategy_params)
        return dict(self._strategy_params)
