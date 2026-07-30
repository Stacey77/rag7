"""Goals: the company's tracked objectives and progress against them."""
import logging

logger = logging.getLogger(__name__)


class Goals:
    """Tracks named goals with target and current progress values."""

    def __init__(self) -> None:
        """Initialize Goals with no goals set."""
        self.goals: dict[str, dict] = {}

    def set_goal(self, name: str, target: float, current: float = 0.0) -> dict:
        """Define or redefine a goal.

        Args:
            name: Goal label (e.g. "Q3 new clients").
            target: Numeric target value.
            current: Current progress value.

        Returns:
            Dict with the stored goal and its completion ratio.
        """
        logger.info("Setting goal '%s' target=%s current=%s", name, target, current)
        self.goals[name] = {"name": name, "target": target, "current": current}
        return self._with_ratio(name)

    def record_progress(self, name: str, current: float) -> dict:
        """Update progress on an existing goal.

        Args:
            name: Goal label to update.
            current: New current progress value.

        Returns:
            Dict with the updated goal and its completion ratio.
        """
        if name not in self.goals:
            raise KeyError(f"Unknown goal: {name}")
        logger.info("Recording progress on '%s': %s", name, current)
        self.goals[name]["current"] = current
        return self._with_ratio(name)

    def _with_ratio(self, name: str) -> dict:
        goal = self.goals[name]
        ratio = goal["current"] / goal["target"] if goal["target"] else 0.0
        return {"status": "ok", "goal": dict(goal), "completion_ratio": round(ratio, 4)}

    def snapshot(self) -> dict:
        """Return the current status of every tracked goal.

        Returns:
            Dict mapping goal name to goal state and completion ratio.
        """
        return {name: self._with_ratio(name) for name in self.goals}
