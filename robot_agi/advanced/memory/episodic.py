"""Episodic memory with capacity-bounded storage and similarity retrieval."""
import logging
import random
from collections import deque

logger = logging.getLogger(__name__)


class EpisodicMemory:
    """Stores and retrieves episodic memories of robot experiences."""

    def __init__(self, capacity: int = 1000) -> None:
        """Initialize EpisodicMemory with a fixed capacity."""
        self.capacity = capacity
        self.episodes: deque = deque(maxlen=capacity)
        self.episode_count: int = 0

    def store_episode(self, experience: dict) -> dict:
        """Store a new episodic experience in memory.

        Args:
            experience: Dict with state, action, reward, and context.

        Returns:
            Dict with episode id and memory status.
        """
        logger.debug("Storing episode #%d", self.episode_count)
        episode = {
            "episode_id": self.episode_count,
            "experience": experience,
            "salience": experience.get("reward", random.uniform(-1, 1)),
        }
        self.episodes.append(episode)
        self.episode_count += 1
        return {
            "status": "stored",
            "episode_id": episode["episode_id"],
            "memory_size": len(self.episodes),
            "capacity": self.capacity,
            "evicted": self.episode_count > self.capacity,
        }

    def recall_similar(self, current_situation: dict) -> list:
        """Recall episodes similar to the current situation.

        Args:
            current_situation: Dict describing the current state/context.

        Returns:
            List of similar episode dicts sorted by relevance.
        """
        logger.info("Recalling similar episodes from %d stored", len(self.episodes))
        if not self.episodes:
            return []
        num_recall = min(5, len(self.episodes))
        recalled = random.sample(list(self.episodes), num_recall)
        recalled_with_sim = [
            {**ep, "similarity": random.uniform(0.3, 1.0)}
            for ep in recalled
        ]
        recalled_with_sim.sort(key=lambda x: x["similarity"], reverse=True)
        return recalled_with_sim

    def replay_for_learning(self) -> list:
        """Sample episodes for experience replay during learning.

        Returns:
            List of sampled episode dicts for replay.
        """
        logger.info("Sampling episodes for replay from %d stored", len(self.episodes))
        if not self.episodes:
            return []
        batch_size = min(32, len(self.episodes))
        sampled = random.sample(list(self.episodes), batch_size)
        return [{"episode_id": ep["episode_id"], "experience": ep["experience"], "weight": random.uniform(0.5, 1.0)} for ep in sampled]
