"""Agent hemisphere: research, create, outreach, follow-up, optimize."""
import logging

from .create import Create
from .follow_up import FollowUp
from .optimize import Optimize
from .outreach import Outreach
from .research import Research

logger = logging.getLogger(__name__)


class AgentSide:
    """Runs the five agent stages as one pipeline against a company edge."""

    def __init__(self) -> None:
        """Initialize the five agent-side stages."""
        self.research = Research()
        self.create = Create()
        self.outreach = Outreach()
        self.follow_up = FollowUp()
        self.optimize = Optimize()

    def execute_pipeline(self, objective: str, edge: dict, hub) -> dict:
        """Run research through optimize for a single objective.

        Args:
            objective: The goal Ingenium is executing toward.
            edge: The company intelligence snapshot from the other hemisphere.
            hub: The connected IntegrationHub both hemispheres share.

        Returns:
            Dict with each stage's output, keyed by stage name, in run order.
        """
        logger.info("Executing agent pipeline for objective: %s", objective)
        research_out = self.research.run(objective, edge, hub)
        create_out = self.create.run(objective, edge, hub, research_out["findings"])
        outreach_out = self.outreach.run(objective, edge, hub, create_out["asset"])
        follow_up_out = self.follow_up.run(objective, hub, outreach_out["sent"])
        optimize_out = self.optimize.run(objective, hub)

        return {
            "research": research_out,
            "create": create_out,
            "outreach": outreach_out,
            "follow_up": follow_up_out,
            "optimize": optimize_out,
        }
