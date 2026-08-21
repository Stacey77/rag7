"""Message: the unit of agent-to-agent (A2A) communication."""
from dataclasses import asdict, dataclass, field


@dataclass
class Message:
    """A single message passed between agents or from the orchestrator.

    Attributes:
        sender: Name of the agent (or "orchestrator") sending the message.
        recipient: Name of the intended recipient agent.
        intent: Short verb describing the message (e.g. "request", "deliver").
        payload: Arbitrary structured content.
    """

    sender: str
    recipient: str
    intent: str
    payload: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Return a JSON-serializable view of the message."""
        return asdict(self)
