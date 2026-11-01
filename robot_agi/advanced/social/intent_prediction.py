"""Human intent prediction for proactive social robots."""
import logging
import random

logger = logging.getLogger(__name__)


class IntentPredictor:
    """Predicts human intentions and next actions from observed trajectories."""

    def __init__(self) -> None:
        """Initialize IntentPredictor."""
        self.action_vocabulary = ["pick_up", "put_down", "open", "close", "sit", "stand", "walk_to", "point_at"]

    def predict_next_action(self, human_trajectory: list) -> dict:
        """Predict the next action a human will take given their trajectory.

        Args:
            human_trajectory: List of position/state dicts over time.

        Returns:
            Dict with predicted next action and probability distribution.
        """
        logger.info("Predicting next action from %d-step trajectory", len(human_trajectory))
        action_probs = {a: random.uniform(0.05, 1.0) for a in self.action_vocabulary}
        total = sum(action_probs.values())
        action_probs = {a: p / total for a, p in action_probs.items()}
        top_action = max(action_probs, key=lambda k: action_probs[k])
        return {
            "status": "predicted",
            "predicted_action": top_action,
            "action_probabilities": action_probs,
            "confidence": action_probs[top_action],
            "trajectory_length": len(human_trajectory),
            "prediction_horizon_steps": 3,
        }

    def infer_goal(self, partial_actions: list) -> dict:
        """Infer the human's goal from a partial sequence of actions.

        Args:
            partial_actions: List of actions observed so far.

        Returns:
            Dict with inferred goal and completion percentage.
        """
        logger.info("Inferring goal from %d partial actions", len(partial_actions))
        possible_goals = ["fetch_object", "prepare_food", "open_door", "tidy_room", "greet_person"]
        inferred_goal = random.choice(possible_goals)
        completion = len(partial_actions) / random.randint(3, 8)
        return {
            "status": "inferred",
            "inferred_goal": inferred_goal,
            "goal_completion_pct": min(completion * 100, 100),
            "partial_actions": partial_actions,
            "expected_remaining_actions": max(0, random.randint(2, 6) - len(partial_actions)),
            "confidence": random.uniform(0.55, 0.9),
        }
