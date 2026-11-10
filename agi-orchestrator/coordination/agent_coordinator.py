"""Agent Coordinator – multi-agent lifecycle management and orchestration.

Maintains a registry of active agents, routes work to them, and provides a
broadcast mechanism for publishing state updates to all registered agents.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")

# Type alias for async agent handler.
AgentHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, Any]]


@dataclass
class AgentRegistration:
    """Metadata for a registered agent.

    Attributes:
        agent_id: Unique identifier for the agent.
        name: Human-readable name.
        capabilities: List of capability tags (e.g. ``["trade", "risk"]``).
        handler: Async callable that processes task payloads.
        metadata: Arbitrary extra attributes.
    """

    agent_id: str
    name: str
    capabilities: list[str] = field(default_factory=list)
    handler: AgentHandler | None = field(default=None, repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentCoordinator:
    """Multi-agent orchestrator supporting registration, coordination, and broadcast.

    Attributes:
        state_manager: Optional shared :class:`GlobalStateManager`.
        _agents: Registry mapping agent IDs to :class:`AgentRegistration`.
    """

    def __init__(self, state_manager: Any | None = None) -> None:
        """Initialise the coordinator.

        Args:
            state_manager: Optional shared state store for reporting.
        """
        self.state_manager = state_manager
        self._agents: dict[str, AgentRegistration] = {}
        log.info("AgentCoordinator initialised")

    def register_agent(self, registration: AgentRegistration) -> str:
        """Add an agent to the coordinator's registry.

        Args:
            registration: :class:`AgentRegistration` describing the agent.

        Returns:
            The ``agent_id`` of the registered agent.

        Raises:
            ValueError: If an agent with the same ``agent_id`` is already registered.
        """
        if registration.agent_id in self._agents:
            raise ValueError(f"Agent '{registration.agent_id}' is already registered")
        self._agents[registration.agent_id] = registration
        log.info(
            "Agent registered",
            agent_id=registration.agent_id,
            name=registration.name,
            capabilities=registration.capabilities,
        )
        return registration.agent_id

    async def coordinate(
        self,
        task: dict[str, Any],
        required_capability: str | None = None,
    ) -> list[Any]:
        """Route *task* to all agents that possess the required capability.

        When *required_capability* is *None* the task is sent to every
        registered agent.  Tasks are dispatched concurrently via
        :func:`asyncio.gather`.

        Args:
            task: Payload dict forwarded to each matching agent's handler.
            required_capability: Optional capability filter.

        Returns:
            List of results returned by each agent's handler (in no guaranteed
            order).

        Raises:
            RuntimeError: If no agents match the requested capability.
        """
        targets = [
            reg
            for reg in self._agents.values()
            if required_capability is None or required_capability in reg.capabilities
        ]
        if not targets:
            raise RuntimeError(
                f"No agents available for capability '{required_capability}'"
            )

        log.info(
            "Coordinating task",
            capability=required_capability,
            agent_count=len(targets),
        )

        async def _dispatch(reg: AgentRegistration) -> Any:
            if reg.handler is None:
                log.warning("Agent has no handler", agent_id=reg.agent_id)
                return None
            try:
                return await reg.handler(task)
            except Exception as exc:  # noqa: BLE001
                log.error("Agent handler error", agent_id=reg.agent_id, error=str(exc))
                return None

        results = await asyncio.gather(*(_dispatch(r) for r in targets))
        return list(results)

    async def broadcast(self, message: dict[str, Any]) -> int:
        """Send *message* to every registered agent's handler in parallel.

        Args:
            message: Payload broadcast to all agents.

        Returns:
            Number of agents that received the message (handler not *None*).
        """
        recipients = [r for r in self._agents.values() if r.handler is not None]
        if not recipients:
            log.debug("Broadcast skipped – no handlers registered")
            return 0

        async def _send(reg: AgentRegistration) -> None:
            try:
                await reg.handler(message)  # type: ignore[misc]
            except Exception as exc:  # noqa: BLE001
                log.error("Broadcast handler error", agent_id=reg.agent_id, error=str(exc))

        await asyncio.gather(*(_send(r) for r in recipients))
        log.info("Broadcast sent", recipient_count=len(recipients))
        return len(recipients)

    def list_agents(self) -> list[AgentRegistration]:
        """Return a snapshot of all currently registered agents.

        Returns:
            List of :class:`AgentRegistration` objects.
        """
        return list(self._agents.values())
