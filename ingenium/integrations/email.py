"""Email integration: sending outreach and follow-up messages."""
import logging

from .base import Integration

logger = logging.getLogger(__name__)


class Email(Integration):
    """Adapter for an email sending/drafting system."""

    name = "email"

    def __init__(self) -> None:
        """Initialize the email adapter with an empty outbox."""
        super().__init__()
        self.outbox: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> dict:
        """Send an email.

        Args:
            to: Recipient address.
            subject: Email subject line.
            body: Email body text.

        Returns:
            Dict describing the sent message.
        """
        self.require_connection()
        message = {"to": to, "subject": subject, "body": body, "status": "sent"}
        self.outbox.append(message)
        logger.info("Email sent to '%s': %s", to, subject)
        return dict(message)

    def snapshot(self) -> dict:
        """Return every message sent so far.

        Returns:
            Dict with the total sent count and the messages themselves.
        """
        return {"total_sent": len(self.outbox), "messages": list(self.outbox)}
