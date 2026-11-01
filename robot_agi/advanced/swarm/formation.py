"""Formation controller for multi-robot formations."""
import logging
import math
import random

logger = logging.getLogger(__name__)

FORMATION_PATTERNS = {
    "line": lambda i, n: [i * 1.0, 0.0],
    "circle": lambda i, n: [math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)],
    "grid": lambda i, n: [float(i % int(n ** 0.5)), float(i // int(n ** 0.5))],
    "wedge": lambda i, n: [float(i), float(abs(i - n // 2))],
}


class FormationController:
    """Controls multi-robot formations with dynamic target computation."""

    def __init__(self) -> None:
        """Initialize FormationController."""
        self.current_formation: str = "line"
        self.num_robots: int = 0
        self.center: list[float] = [0.0, 0.0]

    def set_formation(self, formation_type: str, num_robots: int) -> dict:
        """Set the desired formation type and number of robots.

        Args:
            formation_type: Formation name ('line', 'circle', 'grid', 'wedge').
            num_robots: Number of robots in the formation.

        Returns:
            Dict with formation configuration and slot positions.
        """
        logger.info("Setting formation '%s' for %d robots", formation_type, num_robots)
        self.current_formation = formation_type
        self.num_robots = num_robots
        pattern_fn = FORMATION_PATTERNS.get(formation_type, FORMATION_PATTERNS["line"])
        slots = [pattern_fn(i, max(num_robots, 1)) for i in range(num_robots)]
        return {
            "status": "set",
            "formation_type": formation_type,
            "num_robots": num_robots,
            "slot_positions": slots,
            "formation_width_m": max(s[0] for s in slots) - min(s[0] for s in slots) if slots else 0,
        }

    def compute_targets(self, current_positions: list) -> list:
        """Compute target positions for each robot to reach the formation.

        Args:
            current_positions: List of current robot positions.

        Returns:
            List of target position dicts for each robot.
        """
        logger.info("Computing formation targets for %d robots", len(current_positions))
        pattern_fn = FORMATION_PATTERNS.get(self.current_formation, FORMATION_PATTERNS["line"])
        n = len(current_positions)
        targets = []
        for i, curr_pos in enumerate(current_positions):
            slot = pattern_fn(i, max(n, 1))
            target = [self.center[0] + slot[0], self.center[1] + slot[1]]
            curr = curr_pos if isinstance(curr_pos, list) else [0.0, 0.0]
            dist = math.sqrt(sum((target[j] - curr[j]) ** 2 for j in range(min(len(target), len(curr)))))
            targets.append({
                "robot_index": i,
                "target_position": target,
                "distance_to_target_m": dist,
                "formation_slot": i,
            })
        return targets
