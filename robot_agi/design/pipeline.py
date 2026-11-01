"""Design pipeline: orchestrate the sub-agents to build a robot from a brief."""
import logging

from ..orchestration.knowledge import InMemoryKnowledge
from ..orchestration.orchestrator import Orchestrator
from .agents import KinematicsAgent, MaterialAgent, StructuralAgent, parse_brief

logger = logging.getLogger(__name__)


def design_robot(goal: str) -> dict:
    """Run the full design pipeline for a natural-language goal.

    Args:
        goal: e.g. "6-DOF humanoid service robot arm".

    Returns:
        Dict with the parsed brief, the assembled design (``design``), each
        agent's report, and the full A2A conversation.
    """
    brief = parse_brief(goal)
    knowledge = InMemoryKnowledge()
    orch = Orchestrator()
    orch.register(KinematicsAgent(orch.bus))
    orch.register(StructuralAgent(orch.bus))
    orch.register(MaterialAgent(orch.bus, knowledge))

    result = orch.run(brief, pipeline=["kinematics", "structural", "material"])
    design = result["context"].pop("design")
    logger.info("Designed %s: %d DOF, %.2f kg, %.2f m reach",
                design.name, design.dof(), design.total_mass_kg(), design.reach_m())
    return {
        "brief": brief,
        "reports": result["context"],
        "design": design,
        "conversation": result["conversation"],
    }
