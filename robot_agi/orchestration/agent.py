"""Agent: base class for a specialized worker in the orchestrated system."""
import logging

from .bus import MessageBus
from .knowledge import KnowledgeRetriever
from .message import Message

logger = logging.getLogger(__name__)


class Agent:
    """A specialized agent that contributes to a shared design context.

    Sub-agents override ``run()``. They read prior agents' output from the
    shared ``context`` (a blackboard), optionally consult knowledge, message
    other agents through the bus (recorded for traceability), and return their
    contribution as a dict.
    """

    name = "agent"
    role = "generic"

    def __init__(self, bus: MessageBus, knowledge: KnowledgeRetriever | None = None) -> None:
        """Bind the agent to a bus and an optional knowledge retriever."""
        self.bus = bus
        self.knowledge = knowledge

    def tell(self, recipient: str, intent: str, payload: dict | None = None) -> Message:
        """Send a message to another agent (recorded on the bus)."""
        return self.bus.send(Message(self.name, recipient, intent, payload or {}))

    def ask_knowledge(self, query: str, k: int = 3) -> list[dict]:
        """Retrieve knowledge if a retriever is attached, else return []."""
        return self.knowledge.retrieve(query, k) if self.knowledge else []

    def run(self, brief: dict, context: dict) -> dict:
        """Produce this agent's contribution.

        Args:
            brief: The parsed design brief.
            context: The shared blackboard; keys are prior agents' names.

        Returns:
            This agent's structured contribution (also stored in the context).
        """
        raise NotImplementedError
