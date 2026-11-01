"""Memory consolidation from episodic to semantic memory."""
import logging
import random

logger = logging.getLogger(__name__)


class MemoryConsolidator:
    """Consolidates episodic memories into semantic knowledge."""

    def __init__(self, consolidation_rate: float = 0.1) -> None:
        """Initialize MemoryConsolidator."""
        self.consolidation_rate = consolidation_rate
        self.consolidated_count: int = 0
        self.stats: dict = {}

    def consolidate(self, episodic_memory: object, semantic_memory: object) -> dict:
        """Consolidate relevant episodic memories into semantic memory.

        Args:
            episodic_memory: EpisodicMemory instance with stored episodes.
            semantic_memory: SemanticMemory instance to consolidate into.

        Returns:
            Dict with consolidation statistics and transferred knowledge.
        """
        logger.info("Consolidating episodic to semantic memory")
        episodes = getattr(episodic_memory, "episodes", [])
        num_to_consolidate = max(1, int(len(episodes) * self.consolidation_rate))
        episodes_list = list(episodes)
        to_consolidate = episodes_list[-num_to_consolidate:] if episodes_list else []

        facts_added = 0
        for episode in to_consolidate:
            exp = episode.get("experience", {}) if isinstance(episode, dict) else {}
            if exp and hasattr(semantic_memory, "store_fact"):
                fact = {"concept": exp.get("state", "experience"), "source": "episodic_consolidation", "salience": episode.get("salience", 0)}
                semantic_memory.store_fact(fact)
                facts_added += 1

        self.consolidated_count += facts_added
        self.stats = {
            "consolidated_count": self.consolidated_count,
            "facts_added_this_cycle": facts_added,
            "episodes_processed": num_to_consolidate,
        }
        return {
            "status": "consolidated",
            "facts_added": facts_added,
            "episodes_processed": num_to_consolidate,
            "total_consolidated": self.consolidated_count,
            "consolidation_rate": self.consolidation_rate,
        }

    def get_stats(self) -> dict:
        """Return consolidation statistics.

        Returns:
            Dict with total consolidated facts and processing history.
        """
        logger.info("Returning consolidation stats")
        return {
            "status": "ok",
            "total_consolidated": self.consolidated_count,
            "consolidation_rate": self.consolidation_rate,
            **self.stats,
        }
