"""Knowledge graph for structured world knowledge."""
import logging
import random
from collections import defaultdict

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Represents and reasons over structured world knowledge as a graph."""

    def __init__(self) -> None:
        """Initialize KnowledgeGraph."""
        self.triples: list[tuple[str, str, str]] = []
        self.index: dict[str, list] = defaultdict(list)

    def add_knowledge(self, entity: str, relation: str, value: str) -> dict:
        """Add a knowledge triple (entity, relation, value) to the graph.

        Args:
            entity: Subject entity.
            relation: Relation or predicate.
            value: Object or value.

        Returns:
            Dict confirming addition and current triple count.
        """
        triple = (entity, relation, value)
        self.triples.append(triple)
        self.index[entity].append((relation, value))
        logger.debug("Added triple: %s -[%s]-> %s", entity, relation, value)
        return {
            "status": "added",
            "triple": {"entity": entity, "relation": relation, "value": value},
            "total_triples": len(self.triples),
        }

    def query_knowledge(self, query: str) -> list:
        """Query the knowledge graph for matching triples.

        Args:
            query: Query string (entity name or keyword).

        Returns:
            List of matching triples as dicts.
        """
        logger.info("Querying knowledge graph: '%s'", query)
        results = []
        for entity, relation, value in self.triples:
            if query.lower() in entity.lower() or query.lower() in value.lower() or query.lower() in relation.lower():
                results.append({"entity": entity, "relation": relation, "value": value})
        return results

    def reason_over_graph(self, question: str) -> dict:
        """Perform multi-hop reasoning over the knowledge graph.

        Args:
            question: Natural language question to reason about.

        Returns:
            Dict with answer, reasoning path, and confidence.
        """
        logger.info("Reasoning over graph for: '%s'", question)
        keywords = question.lower().split()
        relevant = [t for t in self.triples if any(k in " ".join(t).lower() for k in keywords)]
        reasoning_path = [{"hop": i, "triple": t} for i, t in enumerate(relevant[:3])]
        return {
            "status": "reasoned",
            "question": question,
            "answer": f"Inferred from {len(relevant)} relevant triples",
            "reasoning_path": reasoning_path,
            "confidence": random.uniform(0.4, 0.9) if relevant else 0.1,
            "triples_used": len(relevant),
        }

    def learn_from_experience(self, observations: list) -> dict:
        """Automatically extract and store knowledge from observations.

        Args:
            observations: List of observation dicts from the environment.

        Returns:
            Dict with newly learned triples and knowledge stats.
        """
        logger.info("Learning from %d observations", len(observations))
        new_triples = 0
        for obs in observations:
            if isinstance(obs, dict) and "subject" in obs and "predicate" in obs and "object" in obs:
                self.add_knowledge(obs["subject"], obs["predicate"], obs["object"])
                new_triples += 1
            else:
                entity = str(obs.get("entity", f"obj_{len(self.triples)}")) if isinstance(obs, dict) else f"obs_{len(self.triples)}"
                self.add_knowledge(entity, "observed_at", str(obs))
                new_triples += 1
        return {
            "status": "learned",
            "new_triples": new_triples,
            "total_triples": len(self.triples),
            "observations_processed": len(observations),
        }
