"""Analytics integration: event tracking and reporting."""
import logging

from .base import Integration

logger = logging.getLogger(__name__)


class Analytics(Integration):
    """Adapter for a product/marketing analytics system."""

    name = "analytics"

    def __init__(self) -> None:
        """Initialize the analytics adapter with an empty event log."""
        super().__init__()
        self.events: list[dict] = []

    def track_event(self, name: str, payload: dict | None = None) -> dict:
        """Track an event.

        Args:
            name: Event name (e.g. "outreach_sent").
            payload: Optional structured event data.

        Returns:
            Dict describing the tracked event.
        """
        self.require_connection()
        event = {"name": name, "payload": payload or {}}
        self.events.append(event)
        logger.info("Tracked analytics event '%s'", name)
        return dict(event)

    def get_report(self) -> dict:
        """Summarize tracked events by name.

        Returns:
            Dict mapping event name to occurrence count.
        """
        self.require_connection()
        counts: dict[str, int] = {}
        for event in self.events:
            counts[event["name"]] = counts.get(event["name"], 0) + 1
        return counts
