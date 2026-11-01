"""Create stage: turn research findings into on-brand assets."""
import logging

logger = logging.getLogger(__name__)


class Create:
    """Produces content/assets that honor the company's brand and knowledge."""

    stage = "create"

    def run(self, objective: str, edge: dict, hub, findings: dict) -> dict:
        """Draft copy for the objective and publish it through the web builder.

        Args:
            objective: The goal Ingenium is executing toward.
            edge: The company intelligence snapshot (strategy, brand, knowledge).
            hub: The IntegrationHub providing connected integrations.
            findings: The Research stage's output.

        Returns:
            Dict with the stage name and the published asset.
        """
        logger.info("Creating assets for objective: %s", objective)
        brand = edge.get("brand", {})
        slug = objective.lower().replace(" ", "-")[:60]
        content = {
            "title": objective,
            "voice": brand.get("voice", ""),
            "tone_words": brand.get("tone_words", []),
            "based_on": findings,
        }
        page = hub.get("web_builder").publish_page(slug, content)
        return {"stage": self.stage, "asset": page}
