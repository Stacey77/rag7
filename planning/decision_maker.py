"""
Decision maker module for the RAG7 planning system.

Implements rule-based decision making with safety checks to select
the optimal action from a set of candidates.
"""

import logging
from typing import Any, Dict, List, Optional


class DecisionMaker:
    """Rule-based decision maker with safety awareness.

    Evaluates candidate actions against the current robot state and
    selects the best action based on a simple scoring heuristic.

    Args:
        config: Optional configuration dictionary.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the decision maker."""
        self._logger = logging.getLogger("rag7.planning.decision")
        self._config = config or {}
        self._safety_threshold = self._config.get("safety_threshold", 0.3)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decide(
        self,
        state: Dict[str, Any],
        options: List[Any],
    ) -> Optional[Any]:
        """Select the best option given the current robot state.

        Safety checks are applied first: if an emergency stop is active
        or an obstacle is closer than the safety threshold only a
        ``stop`` or ``wait`` action is permitted.

        Args:
            state: Current robot state dictionary.
            options: List of candidate action dicts or strings.

        Returns:
            The chosen option, or None if no valid option exists.
        """
        if not options:
            return None

        # Safety gate
        if state.get("is_stopped"):
            safe = [o for o in options if self._is_safe_action(o, emergency=True)]
            if not safe:
                return None
            options = safe

        nearest_obstacle = state.get("nearest_obstacle", float("inf"))
        if nearest_obstacle < self._safety_threshold:
            safe = [o for o in options if self._is_safe_action(o, obstacle=True)]
            options = safe if safe else options

        if not options:
            return None

        # Score each option and return the highest-scoring one
        scored = [(self.evaluate(state, opt), opt) for opt in options]
        scored.sort(key=lambda t: t[0], reverse=True)
        chosen = scored[0][1]
        self._logger.debug("Decision: %s (score=%.3f)", chosen, scored[0][0])
        return chosen

    def evaluate(self, state: Dict[str, Any], action: Any) -> float:
        """Compute a scalar value score for an action given a state.

        Higher scores indicate more desirable actions.

        Args:
            state: Current robot state dictionary.
            action: Action to evaluate (dict or string).

        Returns:
            Float score in the range [0, 1].
        """
        score = 0.5  # Neutral baseline

        action_type = (
            action.get("type", "") if isinstance(action, dict) else str(action)
        )

        # Prefer stop/safety actions when obstacles are near
        nearest = state.get("nearest_obstacle", float("inf"))
        if nearest < self._safety_threshold:
            if action_type in ("stop", "wait", "reverse"):
                score += 0.4
            else:
                score -= 0.3

        # Prefer navigation when goal is known and path is clear
        if state.get("goal_known") and nearest > 1.0:
            if action_type == "navigate":
                score += 0.3

        # Penalise repeated actions
        last_action = state.get("last_action", "")
        if action_type and action_type == last_action:
            score -= 0.1

        return max(0.0, min(1.0, score))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_safe_action(action: Any, emergency: bool = False, obstacle: bool = False) -> bool:
        """Check whether an action is safe to execute.

        Args:
            action: Action dict or string.
            emergency: If True, only allow stop/reset actions.
            obstacle: If True, disallow navigation-type actions.

        Returns:
            True if the action is considered safe.
        """
        action_type = (
            action.get("type", "") if isinstance(action, dict) else str(action)
        )
        if emergency:
            return action_type in ("stop", "reset_stop", "wait")
        if obstacle:
            return action_type not in ("navigate", "grasp", "place")
        return True
