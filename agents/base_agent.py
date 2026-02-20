"""
Base agent module for the rag7 AGI Robotics Framework.

Provides the abstract base class and supporting data structures
for all agents in the system.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentState:
    """Dataclass representing the runtime state of an agent.

    Attributes:
        agent_id: Unique identifier for the agent.
        status: Current status ('idle', 'running', 'error').
        current_task: Description of the current task being executed.
        last_update: Unix timestamp of the last state update.
    """

    agent_id: str
    status: str = "idle"
    current_task: Optional[str] = None
    last_update: float = field(default_factory=time.time)


class BaseAgent(ABC):
    """Abstract base class for all AGI robotic agents.

    All agents in the rag7 framework inherit from this class and must
    implement the perceive-reason-act loop methods.

    Args:
        name: Human-readable name for this agent instance.
        config: Configuration dictionary for agent parameters.
        logger: Optional logger instance; creates a default logger if not provided.
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the base agent with name, config, and optional logger."""
        self._name = name
        self._config = config
        self._logger = logger or logging.getLogger(f"rag7.{name}")
        self._state: Dict[str, Any] = {}
        self._memory: List[Any] = []
        self._tools: List[Any] = []
        self._agent_state = AgentState(agent_id=name)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the agent's name."""
        return self._name

    @property
    def state(self) -> Dict[str, Any]:
        """Return the agent's current state dictionary."""
        return self._state

    @property
    def memory(self) -> List[Any]:
        """Return the agent's memory list."""
        return self._memory

    @property
    def tools(self) -> List[Any]:
        """Return the list of registered tools."""
        return self._tools

    # ------------------------------------------------------------------
    # Abstract methods – must be implemented by subclasses
    # ------------------------------------------------------------------

    @abstractmethod
    def perceive(self, observation: Any) -> Any:
        """Process an observation from the environment.

        Args:
            observation: Raw sensor data or environment observation.

        Returns:
            Processed perception output.
        """

    @abstractmethod
    def reason(self, context: Any) -> Any:
        """Reason over perception data to produce a plan or decision.

        Args:
            context: Contextual information for reasoning.

        Returns:
            Reasoning output (plan, decision, etc.).
        """

    @abstractmethod
    def act(self, action: Any) -> Any:
        """Execute an action in the environment.

        Args:
            action: Action specification to execute.

        Returns:
            Result of the action.
        """

    # ------------------------------------------------------------------
    # Concrete utility methods
    # ------------------------------------------------------------------

    def update_state(self, key: str, value: Any) -> None:
        """Update a single key in the agent's state dictionary.

        Args:
            key: State key to update.
            value: New value for the key.
        """
        self._state[key] = value
        self._agent_state.last_update = time.time()
        self._logger.debug("State updated: %s = %s", key, value)

    def add_to_memory(self, item: Any) -> None:
        """Append an item to the agent's memory.

        Respects the capacity limit defined in config key 'memory_capacity'
        (defaults to 100).  Oldest items are evicted when capacity is exceeded.

        Args:
            item: Item to store in memory.
        """
        capacity = self._config.get("memory_capacity", 100)
        self._memory.append(item)
        if len(self._memory) > capacity:
            self._memory.pop(0)

    def get_memory(self, n: int = 10) -> List[Any]:
        """Return the most recent *n* items from memory.

        Args:
            n: Number of recent items to retrieve (default 10).

        Returns:
            List of the most recent memory items.
        """
        return self._memory[-n:]

    def clear_memory(self) -> None:
        """Clear all items from the agent's memory."""
        self._memory.clear()
        self._logger.debug("Memory cleared for agent '%s'.", self._name)

    def register_tool(self, tool: Any) -> None:
        """Register a callable tool for use by this agent.

        Args:
            tool: Tool object or callable to register.
        """
        self._tools.append(tool)
        self._logger.debug("Tool registered: %s", tool)

    def get_tools(self) -> List[Any]:
        """Return all registered tools.

        Returns:
            List of registered tool objects.
        """
        return list(self._tools)
