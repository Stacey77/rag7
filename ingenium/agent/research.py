"""Research stage: understand the objective before acting on it."""
import logging

logger = logging.getLogger(__name__)


class Research:
    """Gathers signal from CRM, analytics, and the company edge before creating anything."""

    stage = "research"

    def run(self, objective: str, edge: dict, hub) -> dict:
        """Pull current pipeline and analytics data relevant to the objective.

        Args:
            objective: The goal Ingenium is executing toward.
            edge: The company intelligence snapshot (strategy, customers, etc.).
            hub: The IntegrationHub providing connected integrations.

        Returns:
            Dict with the stage name and findings to hand to the next stage.
        """
        logger.info("Researching objective: %s", objective)
        pipeline = hub.get("crm").get_pipeline()
        report = hub.get("analytics").get_report()
        findings = {
            "objective": objective,
            "target_segment": edge.get("customer_data", {}).get("total", 0),
            "pipeline": pipeline,
            "prior_activity": report,
            "priorities": edge.get("strategy", {}).get("priorities", []),
        }
        return {"stage": self.stage, "findings": findings}
