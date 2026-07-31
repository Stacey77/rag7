"""Ingenium: the orchestrator that lets the two hemispheres think, connect, and execute."""
import json
import logging
from pathlib import Path

from ..agent import AgentSide
from ..company_intelligence import CompanyIntelligence
from .integration_hub import IntegrationHub

logger = logging.getLogger(__name__)

STATE_VERSION = 1


class Ingenium:
    """Wires the company intelligence hemisphere to the agent hemisphere.

    Company Intelligence (strategy, customer data, goals, knowledge, brand) is
    the company's edge. The agent side (research, create, outreach, follow-up,
    optimize) is what acts on that edge. The IntegrationHub (CRM, web builder,
    email, finance, analytics, calendar) is the connective tissue both sides
    read from and write through.
    """

    def __init__(self) -> None:
        """Initialize both hemispheres, the shared hub, and an empty run history."""
        self.company_intelligence = CompanyIntelligence()
        self.agent_side = AgentSide()
        self.hub = IntegrationHub()
        self.history: list[dict] = []

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

        The resulting report is appended to ``self.history``.

        Args:
            objective: The goal being pursued (e.g. "Launch Q3 campaign").

        Returns:
            Dict with the company edge used, integration connection status,
            and every agent-side stage's output for this objective.
        """
        thought = self.think(objective)
        connections = self.connect()
        pipeline = self.agent_side.execute_pipeline(objective, thought["edge"], self.hub)
        report = {
            "objective": objective,
            "edge": thought["edge"],
            "integrations": connections,
            "pipeline": pipeline,
        }
        self.history.append(report)
        return report

    def state(self) -> dict:
        """Serialize the persistable state of this Ingenium instance.

        Returns:
            A JSON-serializable dict with the company edge and run history.
            The in-memory integration adapters are not persisted; they
            reconnect fresh on the next ``execute()``.
        """
        return {
            "version": STATE_VERSION,
            "edge": self.company_intelligence.snapshot(),
            "history": list(self.history),
        }

    def load_state(self, state: dict) -> None:
        """Restore the company edge and run history from a ``state()`` dict.

        Args:
            state: A dict shaped like the output of ``state()``.

        Raises:
            ValueError: If the state version is not recognized.
        """
        version = state.get("version")
        if version != STATE_VERSION:
            raise ValueError(f"Unsupported state version: {version!r}")
        self.company_intelligence.restore(state.get("edge", {}))
        self.history = list(state.get("history", []))

    def save(self, path: str | Path) -> Path:
        """Write the current state to a JSON file.

        Args:
            path: Destination file path.

        Returns:
            The resolved Path that was written.
        """
        target = Path(path)
        target.write_text(json.dumps(self.state(), indent=2), encoding="utf-8")
        logger.info("Saved Ingenium state to %s", target)
        return target

    @classmethod
    def load(cls, path: str | Path) -> "Ingenium":
        """Construct an Ingenium instance from a JSON state file.

        Args:
            path: Path to a file previously written by ``save()``.

        Returns:
            A new Ingenium with the company edge and history restored.
        """
        brain = cls()
        brain.load_state(json.loads(Path(path).read_text(encoding="utf-8")))
        logger.info("Loaded Ingenium state from %s", path)
        return brain
