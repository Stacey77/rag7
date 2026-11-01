"""Semantic memory for storing and retrieving factual knowledge."""
import logging
import random
from collections import defaultdict

logger = logging.getLogger(__name__)


class SemanticMemory:
    """Stores general world knowledge as semantic facts."""

    def __init__(self, capacity: int = 100000) -> None:
        """Initialize SemanticMemory."""
        self.capacity = capacity
        self.facts: list[dict] = []
        self.index: dict[str, list[int]] = defaultdict(list)

    def store_fact(self, fact: dict) -> dict:
        """Store a semantic fact in memory.

        Args:
            fact: Dict with concept, property, and value fields.

        Returns:
            Dict with fact id and storage status.
        """
        logger.debug("Storing fact: %s", fact.get("concept", "?"))
        if len(self.facts) >= self.capacity:
            logger.warning("Semantic memory at capacity, evicting oldest fact")
            self.facts.pop(0)
        fact_id = len(self.facts)
        stored = {"fact_id": fact_id, **fact}
        self.facts.append(stored)
        concept = fact.get("concept", "")
        if concept:
            self.index[concept.lower()].append(fact_id)
        return {
            "status": "stored",
            "fact_id": fact_id,
            "total_facts": len(self.facts),
        }

    def retrieve_knowledge(self, query: str) -> list:
        """Retrieve relevant facts from semantic memory.

        Args:
            query: Query string to search for relevant facts.

        Returns:
            List of matching fact dicts.
        """
        logger.info("Retrieving knowledge for: '%s'", query)
        query_lower = query.lower()
        results = []
        for fact in self.facts:
            fact_text = " ".join(str(v) for v in fact.values()).lower()
            if query_lower in fact_text:
                results.append({**fact, "relevance": random.uniform(0.5, 1.0)})
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:10]
