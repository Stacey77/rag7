"""
Behavioural Cloning trainer for the rag7 learning module.

Trains a policy network to imitate expert demonstrations via
supervised learning on state-action pairs.
"""

import logging
import random
from typing import Any, List, Optional, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:

    class PolicyNetwork(nn.Module):
        """Feedforward policy network for behavioural cloning.

        Args:
            state_dim: Input state dimensionality.
            action_dim: Output action dimensionality.
        """

        def __init__(self, state_dim: int, action_dim: int) -> None:
            """Initialize the policy network."""
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(state_dim, 256),
                nn.ReLU(),
                nn.Linear(256, 256),
                nn.ReLU(),
                nn.Linear(256, action_dim),
            )

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            """Forward pass.

            Args:
                x: Input state tensor.

            Returns:
                Action logit tensor.
            """
            return self.net(x)

else:
    PolicyNetwork = None  # type: ignore[assignment,misc]


class BCTrainer:
    """Behavioural Cloning (BC) policy trainer.

    Trains a policy network to mimic expert demonstrations using
    supervised imitation learning.

    Args:
        state_dim: Dimensionality of the state input.
        action_dim: Dimensionality of the action output.
        lr: Learning rate for the Adam optimiser.
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        lr: float = 1e-3,
    ) -> None:
        """Initialize the BC trainer."""
        self._logger = logging.getLogger("rag7.learning.bc")
        self.state_dim = state_dim
        self.action_dim = action_dim
        self._demonstrations: List[Tuple[Any, Any]] = []

        if TORCH_AVAILABLE:
            self.policy = PolicyNetwork(state_dim, action_dim)
            self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
            self.criterion = nn.MSELoss()
        else:
            self._logger.warning("PyTorch not available; BCTrainer in mock mode.")
            self.policy = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_demonstration(self, state: Any, action: Any) -> None:
        """Add a single expert demonstration to the dataset.

        Args:
            state: Expert state observation.
            action: Expert action corresponding to the state.
        """
        self._demonstrations.append((state, action))

    def train(
        self, epochs: int = 10, batch_size: int = 32
    ) -> List[float]:
        """Train the policy network on stored demonstrations.

        Args:
            epochs: Number of training epochs.
            batch_size: Mini-batch size.

        Returns:
            List of per-epoch mean loss values.
        """
        if not self._demonstrations:
            self._logger.warning("No demonstrations available for training.")
            return []

        if not TORCH_AVAILABLE or self.policy is None:
            return [random.random() * 0.1 for _ in range(epochs)]

        import torch

        states = torch.FloatTensor(
            np.asarray([d[0] for d in self._demonstrations], dtype=np.float32)
        )
        actions = torch.FloatTensor(
            np.asarray([d[1] for d in self._demonstrations], dtype=np.float32)
        )
        n = len(self._demonstrations)
        epoch_losses: List[float] = []

        for epoch in range(epochs):
            indices = list(range(n))
            random.shuffle(indices)
            epoch_loss = 0.0
            num_batches = 0

            for start in range(0, n, batch_size):
                batch_idx = indices[start : start + batch_size]
                s_batch = states[batch_idx]
                a_batch = actions[batch_idx]

                pred = self.policy(s_batch)
                loss = self.criterion(pred, a_batch)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                epoch_loss += float(loss.item())
                num_batches += 1

            mean_loss = epoch_loss / max(num_batches, 1)
            epoch_losses.append(mean_loss)
            self._logger.debug("Epoch %d/%d – loss: %.6f", epoch + 1, epochs, mean_loss)

        return epoch_losses

    def predict(self, state: Any) -> Any:
        """Predict an action for a given state.

        Args:
            state: Current state observation (array-like).

        Returns:
            Predicted action as a numpy array.
        """
        if not TORCH_AVAILABLE or self.policy is None:
            return np.zeros(self.action_dim, dtype=np.float32)

        import torch

        state_t = torch.FloatTensor(
            np.asarray(state, dtype=np.float32)
        ).unsqueeze(0)
        with torch.no_grad():
            pred = self.policy(state_t)
        return pred.squeeze().numpy()

    def save(self, path: str) -> None:
        """Save policy weights to disk."""
        if TORCH_AVAILABLE and self.policy is not None:
            import torch

            torch.save(self.policy.state_dict(), path)
            self._logger.info("BC policy saved to '%s'.", path)

    def load(self, path: str) -> None:
        """Load policy weights from disk."""
        if TORCH_AVAILABLE and self.policy is not None:
            import torch

            self.policy.load_state_dict(torch.load(path))
            self._logger.info("BC policy loaded from '%s'.", path)
