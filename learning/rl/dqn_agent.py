"""
DQN (Deep Q-Network) agent for the RAG7 learning module.

Implements experience-replay DQN with epsilon-greedy exploration.
"""

import logging
import random
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:

    class QNetwork(nn.Module):
        """Fully-connected Q-value network.

        Args:
            state_dim: Dimensionality of the state input vector.
            action_dim: Number of discrete actions.
        """

        def __init__(self, state_dim: int, action_dim: int) -> None:
            """Initialize the Q-network."""
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(state_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 128),
                nn.ReLU(),
                nn.Linear(128, action_dim),
            )

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            """Forward pass through the network.

            Args:
                x: Input state tensor of shape (batch, state_dim).

            Returns:
                Q-value tensor of shape (batch, action_dim).
            """
            return self.net(x)

else:
    QNetwork = None  # type: ignore[assignment,misc]


class DQNAgent:
    """Deep Q-Network reinforcement learning agent.

    Implements the DQN algorithm (Mnih et al., 2015) with
    epsilon-greedy exploration and experience replay.

    Args:
        state_dim: Dimensionality of the observation space.
        action_dim: Number of discrete actions.
        lr: Learning rate for the Adam optimiser.
        gamma: Discount factor for future rewards.
        epsilon: Initial exploration probability.
        epsilon_min: Minimum exploration probability.
        epsilon_decay: Multiplicative decay applied each update step.
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        lr: float = 1e-3,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
    ) -> None:
        """Initialize the DQN agent."""
        self._logger = logging.getLogger("rag7.learning.dqn")
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        if TORCH_AVAILABLE:
            self.q_network = QNetwork(state_dim, action_dim)
            self.target_network = QNetwork(state_dim, action_dim)
            self.target_network.load_state_dict(self.q_network.state_dict())
            self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
            self.criterion = nn.MSELoss()
        else:
            self._logger.warning("PyTorch not available; DQN agent in mock mode.")
            self.q_network = None
            self.target_network = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def select_action(self, state: Any) -> int:
        """Select an action using epsilon-greedy policy.

        Args:
            state: Current environment state (array-like).

        Returns:
            Integer action index.
        """
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        if not TORCH_AVAILABLE or self.q_network is None:
            return random.randint(0, self.action_dim - 1)

        import torch

        state_t = torch.FloatTensor(np.asarray(state, dtype=np.float32)).unsqueeze(0)
        with torch.no_grad():
            q_values = self.q_network(state_t)
        return int(q_values.argmax().item())

    def update(self, batch: Dict[str, Any]) -> float:
        """Update the Q-network from a sampled experience batch.

        Args:
            batch: Dictionary with tensor keys: ``states``, ``actions``,
                ``rewards``, ``next_states``, ``dones``.

        Returns:
            Scalar loss value.
        """
        if not TORCH_AVAILABLE or self.q_network is None:
            return 0.0

        import torch

        states = batch["states"]
        actions = batch["actions"]
        rewards = batch["rewards"]
        next_states = batch["next_states"]
        dones = batch["dones"]

        q_current = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze()
        with torch.no_grad():
            q_next = self.target_network(next_states).max(1)[0]
            q_target = rewards + self.gamma * q_next * (1 - dones)

        loss = self.criterion(q_current, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        return float(loss.item())

    def save(self, path: str) -> None:
        """Save the Q-network weights to disk.

        Args:
            path: Destination file path.
        """
        if TORCH_AVAILABLE and self.q_network is not None:
            import torch

            torch.save(self.q_network.state_dict(), path)
            self._logger.info("DQN model saved to '%s'.", path)

    def load(self, path: str) -> None:
        """Load Q-network weights from disk.

        Args:
            path: Source file path.
        """
        if TORCH_AVAILABLE and self.q_network is not None:
            import torch

            self.q_network.load_state_dict(torch.load(path))
            self.target_network.load_state_dict(self.q_network.state_dict())
            self._logger.info("DQN model loaded from '%s'.", path)
