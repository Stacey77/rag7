"""Shared autonomy for blending human and robot control."""
import logging
import random

logger = logging.getLogger(__name__)


class SharedAutonomy:
    """Blends human teleoperation input with autonomous robot assistance."""

    def __init__(self) -> None:
        """Initialize SharedAutonomy."""
        self.autonomy_level: float = 0.5
        self.blend_history: list[dict] = []

    def blend_control(self, human_input: dict, robot_policy: dict) -> dict:
        """Blend human teleoperation input with autonomous robot policy.

        Args:
            human_input: Dict with human control commands and intent.
            robot_policy: Dict with autonomous policy output.

        Returns:
            Dict with blended control command and contribution breakdown.
        """
        logger.info("Blending control: autonomy_level=%.2f", self.autonomy_level)
        h_cmd = human_input.get("command", [0.0, 0.0, 0.0])
        r_cmd = robot_policy.get("command", [0.0, 0.0, 0.0])
        if isinstance(h_cmd, list) and isinstance(r_cmd, list):
            n = min(len(h_cmd), len(r_cmd))
            blended = [(1 - self.autonomy_level) * h_cmd[i] + self.autonomy_level * r_cmd[i] for i in range(n)]
        else:
            blended = [0.0, 0.0, 0.0]
        record = {"autonomy_level": self.autonomy_level, "blended": blended}
        self.blend_history.append(record)
        return {
            "status": "blended",
            "blended_command": blended,
            "human_contribution": 1.0 - self.autonomy_level,
            "robot_contribution": self.autonomy_level,
            "autonomy_level": self.autonomy_level,
            "blend_mode": "linear",
        }

    def adjust_autonomy_level(self, performance: dict) -> dict:
        """Dynamically adjust the autonomy level based on task performance.

        Args:
            performance: Dict with performance metrics and error rates.

        Returns:
            Dict with new autonomy level and adjustment rationale.
        """
        logger.info("Adjusting autonomy level based on performance")
        human_error_rate = performance.get("human_error_rate", random.uniform(0.0, 0.3))
        task_difficulty = performance.get("task_difficulty", random.uniform(0.2, 0.8))
        old_level = self.autonomy_level
        if human_error_rate > 0.2:
            self.autonomy_level = min(1.0, self.autonomy_level + 0.1)
        elif human_error_rate < 0.05:
            self.autonomy_level = max(0.0, self.autonomy_level - 0.1)
        return {
            "status": "adjusted",
            "old_autonomy_level": old_level,
            "new_autonomy_level": self.autonomy_level,
            "adjustment": self.autonomy_level - old_level,
            "human_error_rate": human_error_rate,
            "task_difficulty": task_difficulty,
        }
