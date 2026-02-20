"""
Replay buffer module for the RAG7 learning module.

Provides an efficient circular experience replay buffer for
off-policy reinforcement learning algorithms.
"""

import logging
import random
from collections import deque
from typing import Any, Deque, Dict, List, Tuple

import numpy as np

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class ReplayBuffer:
    """Fixed-capacity circular replay buffer for experience replay.

    Stores (state, action, reward, next_state, done) transitions and
    provides random sampling for training.

    Args:
        capacity: Maximum number of transitions to store.
    """

    def __init__(self, capacity: int = 10_000) -> None:
        """Initialize the replay buffer."""
        self._logger = logging.getLogger("rag7.learning.replay")
        self._capacity = capacity
        self._buffer: Deque[Tuple[Any, Any, float, Any, bool]] = deque(
            maxlen=capacity
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def push(
        self,
        state: Any,
        action: Any,
        reward: float,
        next_state: Any,
        done: bool,
    ) -> None:
        """Add a transition to the buffer.

        When the buffer is full the oldest transition is silently
        evicted.

        Args:
            state: Current observation.
            action: Action taken.
            reward: Observed scalar reward.
            next_state: Resulting observation.
            done: Episode termination flag.
        """
        self._buffer.append((state, action, float(reward), next_state, bool(done)))

    def sample(self, batch_size: int) -> Dict[str, Any]:
        """Sample a random mini-batch of transitions.

        Args:
            batch_size: Number of transitions to sample.

        Returns:
            Dictionary with keys ``states``, ``actions``, ``rewards``,
            ``next_states``, ``dones`` as numpy arrays or torch tensors.

        Raises:
            ValueError: If there are fewer transitions than batch_size.
        """
        if len(self._buffer) < batch_size:
            raise ValueError(
                f"Buffer contains {len(self._buffer)} transitions "
                f"but batch_size is {batch_size}."
            )

        transitions = random.sample(self._buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*transitions)

        states_arr = np.asarray(states, dtype=np.float32)
        actions_arr = np.asarray(actions, dtype=np.int64)
        rewards_arr = np.asarray(rewards, dtype=np.float32)
        next_states_arr = np.asarray(next_states, dtype=np.float32)
        dones_arr = np.asarray(dones, dtype=np.float32)

        if TORCH_AVAILABLE:
            import torch

            return {
                "states": torch.from_numpy(states_arr),
                "actions": torch.from_numpy(actions_arr),
                "rewards": torch.from_numpy(rewards_arr),
                "next_states": torch.from_numpy(next_states_arr),
                "dones": torch.from_numpy(dones_arr),
            }

        return {
            "states": states_arr,
            "actions": actions_arr,
            "rewards": rewards_arr,
            "next_states": next_states_arr,
            "dones": dones_arr,
        }

    def __len__(self) -> int:
        """Return the current number of stored transitions."""
        return len(self._buffer)
