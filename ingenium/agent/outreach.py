"""Outreach stage: put created assets in front of real customers."""
import logging

logger = logging.getLogger(__name__)


class Outreach:
    """Sends the created asset to segmented customers and logs it in the CRM."""

    stage = "outreach"

    def run(self, objective: str, edge: dict, hub, asset: dict) -> dict:
        """Email the relevant customer segment and log the touch in the CRM.

        Args:
            objective: The goal Ingenium is executing toward.
            edge: The company intelligence snapshot (customer data).
            hub: The IntegrationHub providing connected integrations.
            asset: The Create stage's published asset.

        Returns:
            Dict with the stage name and the messages sent.
        """
        logger.info("Running outreach for objective: %s", objective)
        records = edge.get("customer_data", {}).get("records", [])
        sent = []
        for record in records:
            contact_id = record.get("id")
            email_address = record.get("email")
            if not email_address:
                continue
            message = hub.get("email").send(
                to=email_address,
                subject=objective,
                body=f"Check this out: {asset.get('slug')}",
            )
            hub.get("crm").log_activity(contact_id, f"outreach: {objective}", stage="contacted")
            sent.append(message)
        if sent:
            hub.get("analytics").track_event("outreach_sent", {"count": len(sent)})
        return {"stage": self.stage, "sent": sent}
