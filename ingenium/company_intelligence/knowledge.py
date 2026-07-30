"""Knowledge: the company's accumulated facts, docs, and playbooks."""
import logging

logger = logging.getLogger(__name__)


class Knowledge:
    """Simple in-memory knowledge base keyed by topic."""

    def __init__(self) -> None:
        """Initialize Knowledge with an empty knowledge base."""
        self.entries: dict[str, list[str]] = {}

    def add(self, topic: str, fact: str) -> dict:
        """Add a fact under a topic.

        Args:
            topic: Topic label (e.g. "pricing", "onboarding").
            fact: The fact or note to store.

        Returns:
            Dict with all facts currently stored under the topic.
        """
        logger.info("Adding knowledge under topic '%s'", topic)
        self.entries.setdefault(topic, []).append(fact)
        return {"topic": topic, "facts": list(self.entries[topic])}

    def query(self, topic: str) -> dict:
        """Retrieve facts for a topic.

        Args:
            topic: Topic label to look up.

        Returns:
            Dict with facts found for the topic, empty list if none.
        """
        facts = self.entries.get(topic, [])
        logger.debug("Query topic '%s' returned %d facts", topic, len(facts))
        return {"topic": topic, "facts": list(facts)}

    def snapshot(self) -> dict:
        """Return the full knowledge base.

        Returns:
            Dict of every topic and its facts.
        """
        return {topic: list(facts) for topic, facts in self.entries.items()}
