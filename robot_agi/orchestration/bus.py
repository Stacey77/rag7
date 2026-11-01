"""MessageBus: records and routes agent-to-agent messages."""
import logging

from .message import Message

logger = logging.getLogger(__name__)


class MessageBus:
    """A simple in-process bus that logs every message for traceability.

    This is the seam where a real transport (a queue, an A2A protocol, an
    MCP server) would plug in. The default keeps everything in memory so the
    system is fully runnable and testable with no external services.
    """

    def __init__(self) -> None:
        """Initialize the bus with an empty message log."""
        self.log: list[Message] = []

    def send(self, message: Message) -> Message:
        """Record a message on the bus.

        Args:
            message: The Message to send.

        Returns:
            The same Message, for chaining.
        """
        logger.debug("%s -> %s : %s", message.sender, message.recipient, message.intent)
        self.log.append(message)
        return message

    def conversation(self) -> list[dict]:
        """Return the full message log as JSON-serializable dicts."""
        return [m.to_dict() for m in self.log]

    def between(self, a: str, b: str) -> list[Message]:
        """Return messages exchanged between two named agents (either direction)."""
        return [m for m in self.log if {m.sender, m.recipient} == {a, b}]
