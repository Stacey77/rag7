"""
Base Agent module for the Agentic AGI robotics system.
All agents inherit from this base class.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class AgentStatus(Enum):
    """Enumeration of possible agent statuses."""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"
    RECOVERING = "recovering"


@dataclass
class AgentState:
    """Data class representing the current state of an agent."""
    name: str
    status: AgentStatus = AgentStatus.INITIALIZING
    last_heartbeat: float = field(default_factory=time.time)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    error_count: int = 0
    task_count: int = 0
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """Data class representing a message exchanged between agents."""
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: int = 0


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Agentic AGI robotics system.

    Provides common functionality including:
    - State management
    - Message passing
    - Health reporting
    - Lifecycle management
    """

    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.state = AgentState(name=name)
        self.logger = logging.getLogger(f"agent.{name}")
        self._message_handlers: Dict[str, Callable] = {}
        self._message_queue: List[AgentMessage] = []
        self._running = False
        self._connected_agents: Dict[str, "BaseAgent"] = {}

    def connect_agent(self, agent: "BaseAgent") -> None:
        """Register another agent for inter-agent communication."""
        self._connected_agents[agent.name] = agent
        self.logger.debug("Connected to agent: %s", agent.name)

    def send_message(self, recipient: str, message_type: str, payload: Dict[str, Any],
                     priority: int = 0) -> bool:
        """Send a message to another agent."""
        if recipient not in self._connected_agents:
            self.logger.warning("Agent '%s' not found in connected agents", recipient)
            return False

        msg = AgentMessage(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            priority=priority,
        )
        self._connected_agents[recipient].receive_message(msg)
        return True

    def receive_message(self, message: AgentMessage) -> None:
        """Receive and queue a message for processing."""
        self._message_queue.append(message)
        handler = self._message_handlers.get(message.message_type)
        if handler:
            handler(message)
        else:
            self.logger.debug(
                "No handler for message type '%s' from '%s'",
                message.message_type,
                message.sender,
            )

    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a specific message type."""
        self._message_handlers[message_type] = handler

    def get_state(self) -> AgentState:
        """Return the current agent state."""
        self.state.last_heartbeat = time.time()
        return self.state

    def update_status(self, status: AgentStatus) -> None:
        """Update the agent's operational status."""
        old_status = self.state.status
        self.state.status = status
        if old_status != status:
            self.logger.info(
                "Agent '%s' status changed: %s -> %s", self.name, old_status.value, status.value
            )

    def heartbeat(self) -> float:
        """Record and return the current heartbeat timestamp."""
        self.state.last_heartbeat = time.time()
        return self.state.last_heartbeat

    def start(self) -> None:
        """Start the agent."""
        self._running = True
        self.update_status(AgentStatus.HEALTHY)
        self.on_start()
        self.logger.info("Agent '%s' started", self.name)

    def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        self.update_status(AgentStatus.OFFLINE)
        self.on_stop()
        self.logger.info("Agent '%s' stopped", self.name)

    @abstractmethod
    def on_start(self) -> None:
        """Called when agent starts. Override in subclasses."""

    @abstractmethod
    def on_stop(self) -> None:
        """Called when agent stops. Override in subclasses."""

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task. Override in subclasses."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, status={self.state.status.value!r})"
