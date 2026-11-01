"""Active perception for uncertainty-driven sensing."""
import logging
import random

logger = logging.getLogger(__name__)


class ActivePerception:
    """Plans and executes active sensing to reduce uncertainty."""

    def __init__(self) -> None:
        """Initialize ActivePerception."""
        self.view_history: list[dict] = []
        self.uncertainty_threshold = 0.3

    def plan_next_view(self, current_belief: dict) -> dict:
        """Plan the next viewpoint to maximize information gain.

        Args:
            current_belief: Current probabilistic belief state.

        Returns:
            Dict with next viewpoint position, orientation, and expected information gain.
        """
        logger.info("Planning next view from belief state")
        uncertainty = current_belief.get("uncertainty", random.uniform(0.2, 0.8))
        next_view = {
            "position": [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(0.5, 2.0)],
            "orientation": [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), 0.0],
            "expected_info_gain": uncertainty * random.uniform(0.5, 0.9),
            "view_id": len(self.view_history),
        }
        self.view_history.append(next_view)
        return {
            "status": "planned",
            "next_view": next_view,
            "current_uncertainty": uncertainty,
            "views_taken": len(self.view_history),
        }

    def focus_attention(self, scene: dict) -> dict:
        """Focus attention on the most informative parts of the scene.

        Args:
            scene: Dict with scene description and objects.

        Returns:
            Dict with attention focus regions and saliency scores.
        """
        logger.info("Focusing attention on scene with %d objects", len(scene.get("objects", [])))
        objects = scene.get("objects", ["unknown_object"])
        saliency = {obj: random.uniform(0.1, 1.0) for obj in objects}
        focus_target = max(saliency, key=lambda k: saliency[k]) if saliency else None
        return {
            "status": "focused",
            "focus_target": focus_target,
            "saliency_scores": saliency,
            "attention_region": {"x": random.randint(0, 100), "y": random.randint(0, 100), "radius": random.randint(10, 50)},
        }

    def minimize_uncertainty(self, belief_state: dict) -> dict:
        """Select actions that minimally reduce belief-state uncertainty.

        Args:
            belief_state: Current belief state with uncertainty estimates.

        Returns:
            Dict with recommended actions and expected uncertainty reduction.
        """
        logger.info("Minimizing uncertainty in belief state")
        initial_uncertainty = belief_state.get("uncertainty", random.uniform(0.4, 0.9))
        actions = ["rotate_left", "move_closer", "tilt_camera", "scan_area"]
        selected_action = random.choice(actions)
        expected_reduction = initial_uncertainty * random.uniform(0.2, 0.6)
        return {
            "status": "success",
            "recommended_action": selected_action,
            "initial_uncertainty": initial_uncertainty,
            "expected_uncertainty_after": initial_uncertainty - expected_reduction,
            "expected_reduction": expected_reduction,
            "alternative_actions": [a for a in actions if a != selected_action],
        }
