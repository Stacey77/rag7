"""Task-level planner that decomposes missions into executable tasks."""
import logging
import random

logger = logging.getLogger(__name__)


class TaskPlanner:
    """Decomposes mission phases into concrete robot tasks."""

    def __init__(self) -> None:
        """Initialize TaskPlanner."""
        self.task_library: dict[str, list] = {
            "pick": ["locate_object", "plan_grasp", "execute_grasp", "verify_grasp"],
            "place": ["navigate_to_target", "lower_object", "release", "verify_placement"],
            "navigate": ["plan_path", "execute_motion", "avoid_obstacles"],
        }

    def decompose_into_tasks(self, mission: dict) -> list:
        """Decompose a mission into a sequence of executable tasks.

        Args:
            mission: Mission dict with goal and phases.

        Returns:
            List of task dicts with actions and preconditions.
        """
        logger.info("Decomposing mission into tasks")
        goal_type = mission.get("goal", {}).get("type", "pick")
        subtasks = self.task_library.get(goal_type, ["sense", "plan", "act", "verify"])
        tasks = [
            {
                "task_id": i,
                "action": action,
                "preconditions": [f"pre_{action}"],
                "effects": [f"done_{action}"],
                "estimated_duration_s": random.randint(5, 30),
                "priority": i,
            }
            for i, action in enumerate(subtasks)
        ]
        return tasks

    def replan(self, current_state: dict) -> list:
        """Replan the task sequence given the current state.

        Args:
            current_state: Dict describing current world state and failed tasks.

        Returns:
            List of replanned tasks.
        """
        logger.info("Replanning tasks from state: %s", current_state.get("failed_task", "none"))
        failed_task = current_state.get("failed_task", "")
        recovery_tasks = [
            {"task_id": 0, "action": "assess_situation", "priority": 0, "estimated_duration_s": 5},
            {"task_id": 1, "action": f"recover_from_{failed_task or 'failure'}", "priority": 1, "estimated_duration_s": 15},
            {"task_id": 2, "action": "resume_mission", "priority": 2, "estimated_duration_s": 10},
        ]
        return recovery_tasks
