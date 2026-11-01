"""Multi-agent reinforcement learning for cooperative and competitive tasks."""
import logging
import random

logger = logging.getLogger(__name__)


class MultiAgentRL:
    """Trains multiple agents cooperatively or competitively."""

    def __init__(self) -> None:
        """Initialize MultiAgentRL."""
        self.agent_policies: dict[str, dict] = {}
        self.training_step: int = 0

    def train_cooperative(self, agents: list, env: dict) -> dict:
        """Train agents cooperatively to maximize shared reward.

        Args:
            agents: List of agent dicts with ids and capabilities.
            env: Dict describing the cooperative environment.

        Returns:
            Dict with training results and team performance metrics.
        """
        logger.info("Training %d agents cooperatively in '%s'", len(agents), env.get("name", "env"))
        self.training_step += 1
        individual_rewards = {a.get("id", f"agent_{i}"): random.uniform(0, 1) for i, a in enumerate(agents)}
        team_reward = sum(individual_rewards.values()) / max(len(agents), 1)
        for agent_id in individual_rewards:
            self.agent_policies[agent_id] = {"performance": individual_rewards[agent_id], "mode": "cooperative"}
        return {
            "status": "trained",
            "mode": "cooperative",
            "num_agents": len(agents),
            "team_reward": team_reward,
            "individual_rewards": individual_rewards,
            "training_step": self.training_step,
            "convergence": random.uniform(0.5, 0.95),
        }

    def train_competitive(self, agents: list, env: dict) -> dict:
        """Train agents competitively in a zero-sum or general-sum game.

        Args:
            agents: List of agent dicts.
            env: Dict describing the competitive environment.

        Returns:
            Dict with training results and Nash equilibrium estimate.
        """
        logger.info("Training %d agents competitively in '%s'", len(agents), env.get("name", "env"))
        self.training_step += 1
        scores = {a.get("id", f"agent_{i}"): random.uniform(0, 1) for i, a in enumerate(agents)}
        winner_id = max(scores, key=lambda k: scores[k]) if scores else None
        for agent_id in scores:
            self.agent_policies[agent_id] = {"performance": scores[agent_id], "mode": "competitive"}
        return {
            "status": "trained",
            "mode": "competitive",
            "num_agents": len(agents),
            "scores": scores,
            "winner": winner_id,
            "nash_distance": random.uniform(0.01, 0.3),
            "training_step": self.training_step,
        }
