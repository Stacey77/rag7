"""Orchestrator: the central brain that delegates to specialized sub-agents."""
import logging

from .agent import Agent
from .bus import MessageBus

logger = logging.getLogger(__name__)


class Orchestrator:
    """Registers agents and runs them over a shared context in a set order.

    The orchestrator owns the message bus and a blackboard (shared model
    context). It delegates each stage to a specialized agent, which builds on
    the outputs of the agents before it — a hierarchy where one brain
    coordinates a swarm of domain experts.
    """

    def __init__(self, bus: MessageBus | None = None) -> None:
        """Initialize with a fresh (or supplied) message bus."""
        self.bus = bus or MessageBus()
        self.agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """Register a specialized agent by its name."""
        self.agents[agent.name] = agent
        logger.info("Registered agent '%s' (%s)", agent.name, agent.role)

    def run(self, brief: dict, pipeline: list[str]) -> dict:
        """Delegate the brief through an ordered pipeline of agents.

        Args:
            brief: The parsed design brief (what to build).
            pipeline: Agent names to run, in dependency order.

        Returns:
            Dict with the brief, each agent's contribution (keyed by name),
            and the full A2A message log.

        Raises:
            KeyError: If the pipeline names an unregistered agent.
        """
        logger.info("Orchestrating %d-stage pipeline for '%s'", len(pipeline), brief.get("goal", "?"))
        context: dict = {"brief": brief}
        self.bus.send(_orchestrator_msg(pipeline))
        for name in pipeline:
            if name not in self.agents:
                raise KeyError(f"No agent registered under '{name}'")
            agent = self.agents[name]
            self.bus.send(_assign_msg(name, brief))
            context[name] = agent.run(brief, context)
        return {
            "brief": brief,
            "pipeline": list(pipeline),
            "context": {k: v for k, v in context.items() if k != "brief"},
            "conversation": self.bus.conversation(),
        }


def _orchestrator_msg(pipeline: list[str]):
    from .message import Message
    return Message("orchestrator", "all", "plan", {"pipeline": list(pipeline)})


def _assign_msg(name: str, brief: dict):
    from .message import Message
    return Message("orchestrator", name, "assign", {"goal": brief.get("goal")})
