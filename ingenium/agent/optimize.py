"""Optimize stage: close the loop by reading results back into the brain."""
import logging

logger = logging.getLogger(__name__)


class Optimize:
    """Reads analytics and finance results to recommend the next best action."""

    stage = "optimize"

    def run(self, objective: str, hub) -> dict:
        """Summarize performance so far and recommend whether to scale or adjust.

        Args:
            objective: The goal Ingenium is executing toward.
            hub: The IntegrationHub providing connected integrations.

        Returns:
            Dict with the stage name, a performance report, and a recommendation.
        """
        logger.info("Optimizing for objective: %s", objective)
        report = hub.get("analytics").get_report()
        finance = hub.get("finance").get_snapshot()
        sent_count = report.get("outreach_sent", 0)
        recommendation = "scale" if sent_count > 0 else "insufficient_data"
        return {
            "stage": self.stage,
            "report": report,
            "finance": finance,
            "recommendation": recommendation,
        }
