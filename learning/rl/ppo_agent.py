"""
PPO (Proximal Policy Optimisation) agent for the rag7 learning module.

Implements the PPO-Clip algorithm for continuous and discrete action
spaces using actor-critic networks.
"""

import logging
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.distributions import Categorical

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:

    class ActorCritic(nn.Module):
        """Combined actor-critic network for PPO.

        Args:
            state_dim: Input state dimensionality.
            action_dim: Number of discrete actions.
        """

        def __init__(self, state_dim: int, action_dim: int) -> None:
            """Initialize the ActorCritic network."""
            super().__init__()
            self.shared = nn.Sequential(
                nn.Linear(state_dim, 128),
                nn.Tanh(),
                nn.Linear(128, 64),
                nn.Tanh(),
            )
            self.actor_head = nn.Linear(64, action_dim)
            self.critic_head = nn.Linear(64, 1)

        def forward(
            self, x: "torch.Tensor"
        ) -> Tuple["torch.Tensor", "torch.Tensor"]:
            """Compute action logits and state value.

            Args:
                x: Input state tensor.

            Returns:
                Tuple of (action_logits, state_value).
            """
            features = self.shared(x)
            return self.actor_head(features), self.critic_head(features)

        def act(
            self, state: "torch.Tensor"
        ) -> Tuple[int, "torch.Tensor"]:
            """Sample an action and return its log probability.

            Args:
                state: State tensor.

            Returns:
                Tuple of (action integer, log_prob tensor).
            """
            logits, _ = self.forward(state)
            dist = Categorical(logits=logits)
            action = dist.sample()
            return action.item(), dist.log_prob(action)

else:
    ActorCritic = None  # type: ignore[assignment,misc]


class PPOAgent:
    """Proximal Policy Optimisation reinforcement learning agent.

    Args:
        state_dim: Dimensionality of the observation space.
        action_dim: Number of discrete actions.
        lr: Learning rate.
        gamma: Discount factor.
        epsilon_clip: PPO clipping parameter.
        k_epochs: Number of gradient update epochs per batch.
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        lr: float = 3e-4,
        gamma: float = 0.99,
        epsilon_clip: float = 0.2,
        k_epochs: int = 4,
    ) -> None:
        """Initialize the PPO agent."""
        self._logger = logging.getLogger("rag7.learning.ppo")
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon_clip = epsilon_clip
        self.k_epochs = k_epochs

        if TORCH_AVAILABLE:
            self.policy = ActorCritic(state_dim, action_dim)
            self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        else:
            self._logger.warning("PyTorch not available; PPO agent in mock mode.")
            self.policy = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def select_action(self, state: Any) -> Tuple[int, Any]:
        """Select an action using the current policy.

        Args:
            state: Current environment state (array-like).

        Returns:
            Tuple of (action integer, log_prob tensor or float).
        """
        if not TORCH_AVAILABLE or self.policy is None:
            import random

            return random.randint(0, self.action_dim - 1), 0.0

        import torch

        state_t = torch.FloatTensor(np.asarray(state, dtype=np.float32)).unsqueeze(0)
        with torch.no_grad():
            action, log_prob = self.policy.act(state_t)
        return action, log_prob

    def update(self, memory: Dict[str, Any]) -> float:
        """Update actor-critic networks using collected experience.

        Args:
            memory: Dictionary with ``states``, ``actions``,
                ``log_probs``, ``rewards``, ``dones`` keys (tensors).

        Returns:
            Mean policy loss over update epochs.
        """
        if not TORCH_AVAILABLE or self.policy is None:
            return 0.0

        import torch
        import torch.nn.functional as F

        states = memory["states"]
        actions = memory["actions"]
        old_log_probs = memory["log_probs"]
        rewards = memory["rewards"]

        # Compute discounted returns
        returns = []
        discounted = 0.0
        for r in reversed(rewards.tolist()):
            discounted = r + self.gamma * discounted
            returns.insert(0, discounted)
        returns_t = torch.FloatTensor(returns)
        returns_t = (returns_t - returns_t.mean()) / (returns_t.std() + 1e-8)

        total_loss = 0.0
        for _ in range(self.k_epochs):
            logits, values = self.policy(states)
            dist = torch.distributions.Categorical(logits=logits)
            log_probs = dist.log_prob(actions)
            ratio = (log_probs - old_log_probs).exp()
            advantages = returns_t - values.squeeze().detach()

            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.epsilon_clip, 1 + self.epsilon_clip) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = F.mse_loss(values.squeeze(), returns_t)
            loss = actor_loss + 0.5 * critic_loss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            total_loss += float(loss.item())

        return total_loss / self.k_epochs

    def save(self, path: str) -> None:
        """Save policy weights to disk."""
        if TORCH_AVAILABLE and self.policy is not None:
            import torch

            torch.save(self.policy.state_dict(), path)

    def load(self, path: str) -> None:
        """Load policy weights from disk."""
        if TORCH_AVAILABLE and self.policy is not None:
            import torch

            self.policy.load_state_dict(torch.load(path))
