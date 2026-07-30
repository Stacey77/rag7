"""CRM integration: pipeline stages and contact activity."""
import logging

from .base import Integration

logger = logging.getLogger(__name__)


class CRM(Integration):
    """Adapter for a customer relationship management system."""

    name = "crm"

    def __init__(self) -> None:
        """Initialize the CRM adapter with an empty in-memory pipeline."""
        super().__init__()
        self.contacts: dict[str, dict] = {}

    def log_activity(self, contact_id: str, activity: str, stage: str | None = None) -> dict:
        """Log an activity against a contact, optionally moving their stage.

        Args:
            contact_id: Identifier of the contact/deal.
            activity: Description of the activity performed.
            stage: New pipeline stage, if it changed.

        Returns:
            Dict with the contact's updated activity log and stage.
        """
        self.require_connection()
        contact = self.contacts.setdefault(contact_id, {"id": contact_id, "activities": [], "stage": "new"})
        contact["activities"].append(activity)
        if stage:
            contact["stage"] = stage
        logger.info("CRM activity logged for '%s': %s", contact_id, activity)
        return dict(contact)

    def get_pipeline(self) -> dict:
        """Return every contact grouped by current pipeline stage.

        Returns:
            Dict mapping stage name to the list of contact ids in it.
        """
        self.require_connection()
        pipeline: dict[str, list[str]] = {}
        for contact in self.contacts.values():
            pipeline.setdefault(contact["stage"], []).append(contact["id"])
        return pipeline
