"""Calendar integration: scheduling and follow-up timing."""
import logging

from .base import Integration

logger = logging.getLogger(__name__)


class Calendar(Integration):
    """Adapter for a calendar/scheduling system."""

    name = "calendar"

    def __init__(self) -> None:
        """Initialize the calendar adapter with no events scheduled."""
        super().__init__()
        self.events: list[dict] = []

    def schedule_event(self, title: str, when: str, attendees: list[str] | None = None) -> dict:
        """Schedule an event.

        Args:
            title: Event title (e.g. "Follow-up call").
            when: ISO-8601 timestamp or human-readable time slot.
            attendees: Optional list of attendee identifiers.

        Returns:
            Dict describing the scheduled event.
        """
        self.require_connection()
        event = {"title": title, "when": when, "attendees": list(attendees or [])}
        self.events.append(event)
        logger.info("Scheduled event '%s' at %s", title, when)
        return dict(event)

    def get_upcoming(self) -> dict:
        """Return all scheduled events.

        Returns:
            Dict with the total event count and the events themselves.
        """
        self.require_connection()
        return {"total": len(self.events), "events": list(self.events)}
