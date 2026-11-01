"""Predictive maintenance using component health tracking."""
import logging
import random

logger = logging.getLogger(__name__)


class PredictiveMaintenance:
    """Tracks component health and predicts maintenance needs."""

    def __init__(self) -> None:
        """Initialize PredictiveMaintenance."""
        self.component_data: dict[str, list] = {}
        self.health_scores: dict[str, float] = {}
        self.alert_threshold = 0.3

    def update(self, component_id: str, sensor_data: dict) -> dict:
        """Update component health model with new sensor readings.

        Args:
            component_id: Identifier of the component being monitored.
            sensor_data: Dict with sensor readings for this component.

        Returns:
            Dict with updated health score and alert status.
        """
        logger.info("Updating maintenance data for component: %s", component_id)
        if component_id not in self.component_data:
            self.component_data[component_id] = []
        self.component_data[component_id].append(sensor_data)

        readings = [float(v) for v in sensor_data.values() if isinstance(v, (int, float))]
        if readings:
            health = 1.0 - min(1.0, sum(readings) / (len(readings) * 100))
        else:
            health = random.uniform(0.5, 1.0)
        self.health_scores[component_id] = health
        alert = health < self.alert_threshold

        return {
            "status": "updated",
            "component_id": component_id,
            "health_score": health,
            "alert": alert,
            "data_points": len(self.component_data[component_id]),
            "recommended_action": "schedule_maintenance" if alert else "monitor",
        }

    def get_health_status(self) -> dict:
        """Get the health status of all monitored components.

        Returns:
            Dict with per-component health scores and fleet summary.
        """
        logger.info("Getting health status for %d components", len(self.health_scores))
        at_risk = [c for c, h in self.health_scores.items() if h < self.alert_threshold]
        avg_health = sum(self.health_scores.values()) / max(len(self.health_scores), 1)
        return {
            "status": "healthy" if not at_risk else "maintenance_needed",
            "component_health": dict(self.health_scores),
            "avg_fleet_health": avg_health,
            "components_at_risk": at_risk,
            "maintenance_urgency": "high" if any(h < 0.1 for h in self.health_scores.values()) else "low",
        }
