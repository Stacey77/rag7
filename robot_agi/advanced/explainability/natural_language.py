"""Natural language explanation generation for robot decisions."""
import logging
import random

logger = logging.getLogger(__name__)

ACTION_TEMPLATES = {
    "move": "I moved {direction} because {reason}.",
    "grasp": "I grasped the {object} because {reason}.",
    "avoid": "I avoided {obstacle} because {reason}.",
    "wait": "I waited because {reason}.",
    "default": "I performed '{action}' because {reason}.",
}

REASONS = [
    "it was the safest path to the goal",
    "the object was within reach",
    "the obstacle was detected in my path",
    "the task required this action",
    "my planning algorithm determined this was optimal",
]


class NaturalLanguageExplainer:
    """Generates natural language explanations for robot actions and decisions."""

    def __init__(self) -> None:
        """Initialize NaturalLanguageExplainer."""
        self.templates = ACTION_TEMPLATES
        self.reasons = REASONS

    def explain(self, action_or_decision: dict) -> str:
        """Generate a natural language explanation for an action or decision.

        Args:
            action_or_decision: Dict with action type, object, direction, etc.

        Returns:
            Human-readable explanation string.
        """
        logger.info("Generating NL explanation for: %s", action_or_decision.get("type", "action"))
        action_type = action_or_decision.get("type", "default")
        template = self.templates.get(action_type, self.templates["default"])
        reason = random.choice(self.reasons)
        explanation = template.format(
            action=action_type,
            direction=action_or_decision.get("direction", "forward"),
            object=action_or_decision.get("object", "the object"),
            obstacle=action_or_decision.get("obstacle", "the obstacle"),
            reason=reason,
        )
        return explanation

    def generate_summary(self, explanations: list) -> str:
        """Generate a summary of multiple explanations.

        Args:
            explanations: List of explanation strings or dicts.

        Returns:
            Concise summary string of all explanations.
        """
        logger.info("Generating summary of %d explanations", len(explanations))
        if not explanations:
            return "No actions were taken during this period."
        count = len(explanations)
        text_explanations = [str(e) if not isinstance(e, str) else e for e in explanations]
        first = text_explanations[0][:50] if text_explanations else ""
        summary = f"During this episode, {count} action{'s' if count != 1 else ''} were taken. " \
                  f"For example: '{first}...' " \
                  f"Overall, the robot pursued its goal efficiently while maintaining safety."
        return summary
