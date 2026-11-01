"""Runtime safety monitoring for deployed robots."""
import logging
import random

logger = logging.getLogger(__name__)


class RuntimeMonitor:
    """Monitors robot behavior at runtime and detects safety violations."""

    def __init__(self) -> None:
        """Initialize RuntimeMonitor."""
        self.violations: list[dict] = []
        self.monitor_count: int = 0
        self.safety_specs: dict = {
            "max_velocity_ms": 2.0,
            "max_force_N": 50.0,
            "min_human_distance_m": 0.5,
        }

    def monitor(self, state: dict, action: dict) -> dict:
        """Monitor a state-action pair for safety violations.

        Args:
            state: Dict with current robot state and environment info.
            action: Dict with the planned or executed action.

        Returns:
            Dict with monitoring result and any detected violations.
        """
        logger.debug("Monitoring state-action pair #%d", self.monitor_count)
        self.monitor_count += 1
        new_violations = []
        velocity = state.get("velocity_ms", random.uniform(0, 3))
        if velocity > self.safety_specs["max_velocity_ms"]:
            new_violations.append({"type": "velocity_violation", "value": velocity, "limit": self.safety_specs["max_velocity_ms"]})
        force = action.get("force_N", random.uniform(0, 60))
        if force > self.safety_specs["max_force_N"]:
            new_violations.append({"type": "force_violation", "value": force, "limit": self.safety_specs["max_force_N"]})
        human_dist = state.get("human_distance_m", random.uniform(0, 3))
        if human_dist < self.safety_specs["min_human_distance_m"]:
            new_violations.append({"type": "proximity_violation", "value": human_dist, "limit": self.safety_specs["min_human_distance_m"]})
        self.violations.extend(new_violations)
        return {
            "status": "safe" if not new_violations else "violation_detected",
            "monitor_count": self.monitor_count,
            "new_violations": new_violations,
            "total_violations": len(self.violations),
            "recommended_action": "stop_immediately" if new_violations else "continue",
        }

    def get_violations(self) -> list:
        """Get all recorded safety violations.

        Returns:
            List of all violation dicts recorded during monitoring.
        """
        logger.info("Returning %d total violations", len(self.violations))
        return list(self.violations)
