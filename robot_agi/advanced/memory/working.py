"""Working memory for maintaining active goals and context."""
import logging

logger = logging.getLogger(__name__)


class WorkingMemory:
    """Short-term working memory maintaining active goals and current context."""

    def __init__(self, max_goals: int = 7) -> None:
        """Initialize WorkingMemory with Miller's Law capacity."""
        self.max_goals = max_goals
        self.goals: list[dict] = []
        self.context: dict = {}

    def update_goals(self, new_goal: dict) -> dict:
        """Add or update a goal in working memory.

        Args:
            new_goal: Dict with goal specification and priority.

        Returns:
            Dict with current goals and capacity status.
        """
        logger.info("Updating goals: adding '%s'", new_goal.get("name", "goal"))
        if len(self.goals) >= self.max_goals:
            min_priority = min(self.goals, key=lambda g: g.get("priority", 0))
            self.goals.remove(min_priority)
            evicted = min_priority.get("name", "?")
        else:
            evicted = None

        self.goals.append(new_goal)
        self.goals.sort(key=lambda g: g.get("priority", 0), reverse=True)
        return {
            "status": "updated",
            "current_goals": len(self.goals),
            "max_goals": self.max_goals,
            "evicted_goal": evicted,
            "goals": [g.get("name", str(g)) for g in self.goals],
        }

    def maintain_context(self, context: dict) -> dict:
        """Update and maintain the current context in working memory.

        Args:
            context: Dict with current situational context.

        Returns:
            Dict with updated context state.
        """
        logger.debug("Maintaining context with %d items", len(context))
        self.context.update(context)
        if len(self.context) > 50:
            keys_to_remove = list(self.context.keys())[:len(self.context) - 50]
            for k in keys_to_remove:
                del self.context[k]
        return {
            "status": "maintained",
            "context_size": len(self.context),
            "context_keys": list(self.context.keys()),
        }

    def get_current_goals(self) -> list:
        """Get the list of currently active goals.

        Returns:
            List of active goal dicts sorted by priority.
        """
        logger.debug("Retrieving %d current goals", len(self.goals))
        return list(self.goals)
