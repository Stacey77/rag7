"""Curriculum learning for progressive skill acquisition."""
import logging
import random

logger = logging.getLogger(__name__)


class CurriculumGenerator:
    """Generates and adapts learning curricula for progressive training."""

    def __init__(self) -> None:
        """Initialize CurriculumGenerator."""
        self.current_difficulty = 0.1
        self.performance_history: list[float] = []

    def generate_curriculum(self, goal_task: dict) -> list:
        """Generate a progressive curriculum leading to a goal task.

        Args:
            goal_task: Dict with the target task and its requirements.

        Returns:
            List of curriculum stage dicts from easiest to goal task.
        """
        logger.info("Generating curriculum for goal task: %s", goal_task.get("name", "?"))
        num_stages = random.randint(4, 8)
        curriculum = []
        for i in range(num_stages):
            difficulty = (i + 1) / num_stages
            stage = {
                "stage": i,
                "difficulty": difficulty,
                "task_variant": f"{goal_task.get('name', 'task')}_difficulty_{difficulty:.1f}",
                "success_threshold": 0.7 + 0.03 * i,
                "max_episodes": int(500 / (i + 1)),
                "is_goal_task": i == num_stages - 1,
            }
            curriculum.append(stage)
        return curriculum

    def adapt_difficulty(self, performance: dict) -> dict:
        """Adapt curriculum difficulty based on recent performance.

        Args:
            performance: Dict with recent success rate and episode count.

        Returns:
            Dict with new difficulty level and adaptation rationale.
        """
        logger.info("Adapting difficulty based on performance")
        success_rate = performance.get("success_rate", random.uniform(0.3, 0.9))
        self.performance_history.append(success_rate)
        if success_rate > 0.8:
            self.current_difficulty = min(1.0, self.current_difficulty + 0.1)
            direction = "increased"
        elif success_rate < 0.4:
            self.current_difficulty = max(0.05, self.current_difficulty - 0.1)
            direction = "decreased"
        else:
            direction = "unchanged"
        return {
            "status": "adapted",
            "new_difficulty": self.current_difficulty,
            "previous_success_rate": success_rate,
            "adaptation_direction": direction,
            "performance_trend": "improving" if len(self.performance_history) > 1 and self.performance_history[-1] > self.performance_history[-2] else "stable",
        }
