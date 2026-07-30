"""Ingenium: the orchestrator that lets the two hemispheres think, connect, and execute."""
import logging

from ..agent import AgentSide
from ..company_intelligence import CompanyIntelligence
from .integration_hub import IntegrationHub

logger = logging.getLogger(__name__)


class Ingenium:
    """Wires the company intelligence hemisphere to the agent hemisphere.

    Company Intelligence (strategy, customer data, goals, knowledge, brand) is
    the company's edge. The agent side (research, create, outreach, follow-up,
    optimize) is what acts on that edge. The IntegrationHub (CRM, web builder,
    email, finance, analytics, calendar) is the connective tissue both sides
    read from and write through.
    """

    def __init__(self) -> None:
        """Initialize both hemispheres and the shared integration hub."""
        self.company_intelligence = CompanyIntelligence()
        self.agent_side = AgentSide()
        self.hub = IntegrationHub()

    def think(self, objective: str) -> dict:
        """Build the shared context ("company edge") an objective will act on.

        Args:
            objective: The goal being pursued (e.g. "Launch Q3 campaign").

        Returns:
            Dict with the objective and the current company intelligence snapshot.
        """
        logger.info("Thinking about objective: %s", objective)
        return {"objective": objective, "edge": self.company_intelligence.snapshot()}

    def connect(self) -> dict:
        """Connect every integration so both hemispheres can read and act through them.

        Returns:
            Dict mapping integration name to its connection status.
        """
        logger.info("Connecting integration layer")
        return self.hub.connect_all()

    def execute(self, objective: str) -> dict:
        """Think, connect, and execute the agent pipeline for an objective.

        Args:
            objective: The goal being pursued (e.g. "Launch Q3 campaign").

        Returns:
            Dict with the company edge used, integration connection status,
            and every agent-side stage's output for this objective.
        """
        thought = self.think(objective)
        connections = self.connect()
        pipeline = self.agent_side.execute_pipeline(objective, thought["edge"], self.hub)
        return {
            "objective": objective,
            "edge": thought["edge"],
            "integrations": connections,
            "pipeline": pipeline,
        }
