"""
Coordination agent module for the RAG7 AGI Robotics Framework.

Manages multi-agent task allocation and coordination across a fleet
of robotic agents.
"""

import logging
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent


class CoordinationAgent(BaseAgent):
    """Agent responsible for multi-robot task coordination.

    Maintains a registry of managed agents and allocates tasks to them
    using a capability-based strategy.

    Args:
        config: Coordination agent configuration dictionary.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the coordination agent."""
        super().__init__(
            name="coordination_agent",
            config=config,
            logger=logging.getLogger("rag7.coordination"),
        )
        self._agents: List[BaseAgent] = []
        self._task_allocations: Dict[str, str] = {}  # task_id -> agent_name
        self._strategy = config.get("task_allocation_strategy", "capability_based")
        self._max_robots = config.get("max_robots", 10)

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def perceive(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Update multi-agent state from an observation.

        Args:
            observation: Dictionary containing agent status updates.

        Returns:
            Current aggregated multi-agent state.
        """
        if "agent_updates" in observation:
            for agent_name, status in observation["agent_updates"].items():
                self.update_state(f"agent_{agent_name}_status", status)
        return self.get_agent_status()

    def reason(self, context: Any) -> Dict[str, Any]:
        """Determine optimal task allocation across managed agents.

        Args:
            context: Dictionary with a ``tasks`` key listing task dicts,
                or a single task dict.

        Returns:
            Allocation plan dictionary.
        """
        tasks = []
        if isinstance(context, dict):
            tasks = context.get("tasks", [context] if "task_type" in context else [])
        elif isinstance(context, list):
            tasks = context

        if not tasks:
            return {"status": "no_tasks", "allocations": {}}

        allocations = self.coordinate(tasks)
        return {"status": "allocated", "allocations": allocations}

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate agents according to the given action.

        Args:
            action: Dictionary with ``type`` key.
                Supported: ``allocate``, ``status``, ``broadcast``.

        Returns:
            Result dictionary.
        """
        action_type = action.get("type", "")

        if action_type == "allocate":
            task = action.get("task", {})
            agent = self.allocate_task(task, self._agents)
            return {"status": "allocated", "agent": agent.name if agent else None}

        if action_type == "status":
            return {"status": "ok", "agent_status": self.get_agent_status()}

        if action_type == "broadcast":
            message = action.get("message", {})
            results = []
            for agent in self._agents:
                try:
                    result = agent.perceive(message)
                    results.append({"agent": agent.name, "result": result})
                except Exception as exc:  # noqa: BLE001
                    results.append({"agent": agent.name, "error": str(exc)})
            return {"status": "broadcasted", "results": results}

        return {"status": "unknown_action"}

    # ------------------------------------------------------------------
    # Public coordination API
    # ------------------------------------------------------------------

    def register_agent(self, agent: BaseAgent) -> None:
        """Add an agent to the managed pool.

        Args:
            agent: Agent instance to register.

        Raises:
            ValueError: If the pool is already at maximum capacity.
        """
        if len(self._agents) >= self._max_robots:
            raise ValueError(
                f"Maximum agent capacity ({self._max_robots}) reached."
            )
        self._agents.append(agent)
        self._logger.info("Agent '%s' registered.", agent.name)

    def allocate_task(
        self,
        task: Dict[str, Any],
        agents: Optional[List[BaseAgent]] = None,
    ) -> Optional[BaseAgent]:
        """Allocate a task to the most suitable agent.

        Uses capability-based matching when the strategy is
        ``capability_based``; otherwise assigns round-robin.

        Args:
            task: Task specification dictionary with optional ``requires``
                key listing required capability strings.
            agents: Optional list of candidate agents.  Defaults to the
                full registered pool.

        Returns:
            The selected agent, or None if no suitable agent is found.
        """
        candidate_pool = agents if agents is not None else self._agents
        if not candidate_pool:
            self._logger.warning("No agents available for task allocation.")
            return None

        required = task.get("requires", [])

        if self._strategy == "capability_based" and required:
            for agent in candidate_pool:
                agent_state = agent.state
                capabilities = agent_state.get("capabilities", [])
                if all(cap in capabilities for cap in required):
                    self._record_allocation(task, agent)
                    return agent

        # Default: least loaded agent (smallest memory size as proxy)
        selected = min(candidate_pool, key=lambda a: len(a.memory))
        self._record_allocation(task, selected)
        return selected

    def coordinate(
        self, task_list: List[Dict[str, Any]]
    ) -> Dict[str, Optional[str]]:
        """Allocate each task in the list to a managed agent.

        Args:
            task_list: List of task specification dictionaries.

        Returns:
            Dictionary mapping task ID strings to agent name strings (or
            None if no agent was available).
        """
        allocations: Dict[str, Optional[str]] = {}
        for task in task_list:
            task_id = str(task.get("task_id", id(task)))
            agent = self.allocate_task(task)
            allocations[task_id] = agent.name if agent else None
        self._logger.info("Task coordination complete: %s", allocations)
        return allocations

    def get_agent_status(self) -> Dict[str, Any]:
        """Return a status summary for all registered agents.

        Returns:
            Dictionary mapping agent names to their state dicts.
        """
        return {agent.name: dict(agent.state) for agent in self._agents}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _record_allocation(self, task: Dict[str, Any], agent: BaseAgent) -> None:
        """Record a task-to-agent allocation.

        Args:
            task: Task specification.
            agent: Assigned agent.
        """
        task_id = str(task.get("task_id", id(task)))
        self._task_allocations[task_id] = agent.name
        self._logger.debug("Task '%s' allocated to agent '%s'.", task_id, agent.name)
