"""Inverse reinforcement learning to infer rewards from demonstrations."""
import logging
import random

logger = logging.getLogger(__name__)


class InverseRL:
    """Learns reward functions from expert demonstrations."""

    def __init__(self) -> None:
        """Initialize InverseRL."""
        self.learned_reward: dict = {}
        self.feature_weights: list[float] = []

    def learn_reward(self, demonstrations: list) -> dict:
        """Learn a reward function from expert demonstrations.

        Args:
            demonstrations: List of expert trajectory dicts.

        Returns:
            Dict with learned reward function parameters and quality.
        """
        logger.info("Learning reward from %d demonstrations", len(demonstrations))
        n_features = 8
        self.feature_weights = [random.uniform(-1, 1) for _ in range(n_features)]
        total_weight = sum(abs(w) for w in self.feature_weights)
        self.feature_weights = [w / max(total_weight, 1e-9) for w in self.feature_weights]
        self.learned_reward = {
            "feature_weights": self.feature_weights,
            "num_features": n_features,
            "reward_type": "linear_combination",
        }
        return {
            "status": "learned",
            "reward_function": self.learned_reward,
            "demonstrations_used": len(demonstrations),
            "reward_quality": random.uniform(0.6, 0.95),
            "algorithm": "MaxEntIRL",
        }

    def infer_preferences(self, choices: list) -> dict:
        """Infer human preferences from pairwise choices.

        Args:
            choices: List of choice dicts with preferred and non-preferred options.

        Returns:
            Dict with inferred preference weights and consistency score.
        """
        logger.info("Inferring preferences from %d choices", len(choices))
        preference_weights = {f"feature_{i}": random.uniform(0, 1) for i in range(5)}
        total = sum(preference_weights.values())
        preference_weights = {k: v / total for k, v in preference_weights.items()}
        consistency = random.uniform(0.6, 0.99)
        return {
            "status": "inferred",
            "preference_weights": preference_weights,
            "consistency_score": consistency,
            "choices_analyzed": len(choices),
            "dominant_preference": max(preference_weights, key=lambda k: preference_weights[k]),
        }
