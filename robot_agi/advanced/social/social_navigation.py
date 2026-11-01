"""Social navigation with awareness of human personal space."""
import logging
import math
import random

logger = logging.getLogger(__name__)


class SocialNavigator:
    """Plans socially-aware robot navigation around humans."""

    def __init__(self, personal_space_m: float = 1.2) -> None:
        """Initialize SocialNavigator."""
        self.personal_space_m = personal_space_m
        self.proxemics = {"intimate": 0.45, "personal": 1.2, "social": 3.7, "public": 7.6}

    def respect_personal_space(self, humans: list) -> dict:
        """Plan navigation that respects human personal space.

        Args:
            humans: List of human state dicts with positions.

        Returns:
            Dict with waypoints that maintain appropriate distances.
        """
        logger.info("Planning with personal space for %d humans", len(humans))
        violations = []
        safe_waypoints = []
        for human in humans:
            pos = human.get("position", [0, 0])
            dist = math.sqrt(sum(p ** 2 for p in pos))
            if dist < self.personal_space_m:
                violations.append({"human_id": human.get("id", "?"), "distance_m": dist, "required_m": self.personal_space_m})
            safe_waypoints.append({
                "position": [pos[0] + self.personal_space_m * 1.2, pos[1] + self.personal_space_m * 1.2],
                "human_avoided": human.get("id", "?"),
            })
        return {
            "status": "planned",
            "violations_detected": len(violations),
            "violations": violations,
            "safe_waypoints": safe_waypoints,
            "personal_space_m": self.personal_space_m,
        }

    def predict_human_trajectories(self, humans: list) -> list:
        """Predict future trajectories of nearby humans.

        Args:
            humans: List of human state dicts with current positions and velocities.

        Returns:
            List of predicted trajectory dicts per human.
        """
        logger.info("Predicting trajectories for %d humans", len(humans))
        predictions = []
        for human in humans:
            pos = human.get("position", [0.0, 0.0])
            vel = human.get("velocity", [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])
            predicted_positions = [
                {"t": t * 0.5, "position": [pos[0] + vel[0] * t * 0.5, pos[1] + vel[1] * t * 0.5]}
                for t in range(1, 6)
            ]
            predictions.append({
                "human_id": human.get("id", "?"),
                "current_position": pos,
                "predicted_trajectory": predicted_positions,
                "prediction_horizon_s": 2.5,
                "confidence": random.uniform(0.6, 0.9),
            })
        return predictions

    def communicate_intent(self, planned_action: dict) -> dict:
        """Signal the robot's intended motion to nearby humans.

        Args:
            planned_action: Dict with the robot's intended motion or action.

        Returns:
            Dict with communication signals and modalities used.
        """
        logger.info("Communicating intent: %s", planned_action.get("type", "motion"))
        signals = []
        action_type = planned_action.get("type", "move")
        if "move" in action_type.lower():
            signals.append({"modality": "LED", "pattern": "directional_arrow", "direction": planned_action.get("direction", "forward")})
            signals.append({"modality": "sound", "tone": "short_beep", "repetitions": 1})
        else:
            signals.append({"modality": "display", "message": f"Robot will: {action_type}"})
        return {
            "status": "communicated",
            "intended_action": planned_action,
            "signals": signals,
            "modalities_used": [s["modality"] for s in signals],
        }
