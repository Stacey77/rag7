"""Follow-up stage: make sure outreach doesn't go cold."""
import logging

logger = logging.getLogger(__name__)


class FollowUp:
    """Schedules follow-up touchpoints for everyone reached during outreach."""

    stage = "follow_up"

    def run(self, objective: str, hub, sent: list[dict]) -> dict:
        """Schedule a calendar follow-up for each outreach message sent.

        Args:
            objective: The goal Ingenium is executing toward.
            hub: The IntegrationHub providing connected integrations.
            sent: The Outreach stage's list of sent messages.

        Returns:
            Dict with the stage name and the scheduled follow-ups.
        """
        logger.info("Scheduling follow-ups for objective: %s", objective)
        scheduled = []
        for message in sent:
            event = hub.get("calendar").schedule_event(
                title=f"Follow up: {objective}",
                when="+3d",
                attendees=[message["to"]],
            )
            scheduled.append(event)
        return {"stage": self.stage, "scheduled": scheduled}
