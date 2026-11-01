"""Proactive assistance for anticipating and meeting human needs."""
import logging
import random

logger = logging.getLogger(__name__)


class ProactiveAssistant:
    """Anticipates human needs and prepares assistance proactively."""

    def __init__(self) -> None:
        """Initialize ProactiveAssistant."""
        self.assistance_history: list[dict] = []
        self.anticipation_horizon_s = 5.0

    def anticipate_needs(self, human_activity: dict) -> dict:
        """Anticipate what the human will need based on current activity.

        Args:
            human_activity: Dict with current human activity and context.

        Returns:
            Dict with predicted needs and preparation priorities.
        """
        logger.info("Anticipating needs for activity: %s", human_activity.get("type", "unknown"))
        activity = human_activity.get("type", "working")
        needs_map = {
            "cooking": ["fetch_ingredient", "hold_bowl", "hand_utensil"],
            "assembly": ["hand_tool", "hold_part", "inspect_joint"],
            "working": ["fetch_document", "hold_item", "provide_support"],
        }
        predicted_needs = needs_map.get(activity, ["provide_support", "fetch_item"])
        priorities = {need: random.uniform(0.3, 1.0) for need in predicted_needs}
        return {
            "status": "anticipated",
            "activity": activity,
            "predicted_needs": predicted_needs,
            "need_priorities": priorities,
            "top_need": max(priorities, key=lambda k: priorities[k]),
            "anticipation_confidence": random.uniform(0.5, 0.9),
        }

    def prepare_assistance(self, predicted_need: dict) -> dict:
        """Prepare the robot to provide the predicted assistance.

        Args:
            predicted_need: Dict with need type and priority.

        Returns:
            Dict with preparation steps and readiness status.
        """
        logger.info("Preparing assistance for: %s", predicted_need.get("type", "?"))
        need_type = predicted_need.get("type", "support")
        preparation_steps = {
            "fetch_item": ["navigate_to_item", "grasp_item", "navigate_to_human"],
            "hold_part": ["position_arm", "open_gripper", "wait_for_item"],
            "support": ["move_to_position", "adopt_ready_pose"],
        }
        steps = preparation_steps.get(need_type, ["position_for_assistance"])
        record = {"need": need_type, "steps": steps, "ready": True}
        self.assistance_history.append(record)
        return {
            "status": "prepared",
            "need_type": need_type,
            "preparation_steps": steps,
            "ready": True,
            "preparation_time_s": random.uniform(1.0, 5.0),
        }
