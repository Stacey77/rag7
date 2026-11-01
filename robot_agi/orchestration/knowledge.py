"""Knowledge retrieval interface — the plug-in point for RAG / vector DBs."""
import logging

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """Abstract interface agents use to look up domain knowledge.

    The default implementation is an in-memory keyword store so the system
    runs with no external services. To use LlamaIndex over a vector database
    (Pinecone, ChromaDB, …), implement ``retrieve()`` against that backend and
    pass the instance to the agents — nothing else in the system changes.
    """

    def retrieve(self, query: str, k: int = 3) -> list[dict]:
        """Return up to ``k`` knowledge entries relevant to ``query``."""
        raise NotImplementedError


class InMemoryKnowledge(KnowledgeRetriever):
    """A tiny keyword-matched knowledge base with sensible robotics defaults."""

    DEFAULTS = [
        {"topic": "material", "text": "Steel: high strength, heavy; good for load-bearing bases."},
        {"topic": "material", "text": "Aluminium 6061: light, stiff; good for mid links."},
        {"topic": "material", "text": "Carbon-fibre composite: very light and stiff; good for distal links."},
        {"topic": "joint", "text": "Revolute joints rotate about one axis; typical arm range -pi..pi."},
        {"topic": "kinematics", "text": "A 6-DOF arm reaches any position and orientation in its workspace."},
        {"topic": "sensor", "text": "Encoders at each joint report angle; an IMU at the base reports orientation."},
    ]

    def __init__(self, entries: list[dict] | None = None) -> None:
        """Initialize with default robotics knowledge (or a custom list)."""
        self.entries = list(entries if entries is not None else self.DEFAULTS)

    def retrieve(self, query: str, k: int = 3) -> list[dict]:
        """Return entries whose topic or text share a word with the query."""
        words = {w for w in query.lower().split() if len(w) > 2}
        scored = []
        for entry in self.entries:
            hay = (entry["topic"] + " " + entry["text"]).lower()
            score = sum(1 for w in words if w in hay)
            if score:
                scored.append((score, entry))
        scored.sort(key=lambda s: s[0], reverse=True)
        return [entry for _, entry in scored[:k]]
