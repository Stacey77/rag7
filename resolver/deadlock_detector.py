"""
Deadlock detection and breaking for the Resolver Agent.

Detects circular waits, resource deadlocks, and task deadlocks,
then applies breaking strategies to restore progress.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


logger = logging.getLogger(__name__)


@dataclass
class Deadlock:
    """Represents a detected deadlock."""
    deadlock_type: str
    involved_agents: List[str]
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    detected_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deadlock_type": self.deadlock_type,
            "involved_agents": self.involved_agents,
            "description": self.description,
            "details": self.details,
            "detected_at": self.detected_at,
        }


class DeadlockDetector:
    """
    Detect and break deadlocks in the multi-agent system.

    Deadlock types handled:
    - Circular dependencies (A waits for B, B waits for A)
    - Resource deadlocks   (all agents waiting for held resources)
    - Task deadlocks       (tasks cannot proceed)
    """

    TIMEOUT_THRESHOLD = 30.0  # seconds a wait may last before suspecting deadlock

    def __init__(self):
        # wait_graph[agent] = set of agents this agent is waiting for
        self._wait_graph: Dict[str, Set[str]] = {}
        # resource_holders[resource] = agent currently holding it
        self._resource_holders: Dict[str, str] = {}
        # resource_waiters[resource] = list of agents waiting for it
        self._resource_waiters: Dict[str, List[str]] = {}
        self._detected_deadlocks: List[Deadlock] = []

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def update_wait_graph(self, agent: str, waiting_for: List[str]) -> None:
        """Record that *agent* is waiting for the listed agents."""
        self._wait_graph[agent] = set(waiting_for)

    def update_resource_state(
        self, resource: str, holder: Optional[str], waiters: Optional[List[str]] = None
    ) -> None:
        """Update resource holder and waiter information."""
        if holder:
            self._resource_holders[resource] = holder
        elif resource in self._resource_holders:
            del self._resource_holders[resource]
        self._resource_waiters[resource] = waiters or []

    def detect(self) -> Optional[Dict[str, Any]]:
        """Run all deadlock detection heuristics and return the first found."""
        deadlock = self.detect_circular_wait()
        if deadlock:
            return deadlock
        return self.detect_resource_deadlock()

    def detect_circular_wait(self) -> Optional[Dict[str, Any]]:
        """Detect circular waiting chains in the wait graph (DFS cycle detection)."""
        cycle = self._find_cycle()
        if cycle:
            deadlock = Deadlock(
                deadlock_type="circular_wait",
                involved_agents=cycle,
                description=f"Circular wait detected: {' -> '.join(cycle)}",
                details={"cycle": cycle},
            )
            self._detected_deadlocks.append(deadlock)
            logger.warning("Circular wait deadlock detected: %s", cycle)
            return deadlock.to_dict()
        return None

    def detect_resource_deadlock(self) -> Optional[Dict[str, Any]]:
        """Detect resource deadlocks where every waiter is also a holder."""
        for resource, waiters in self._resource_waiters.items():
            holder = self._resource_holders.get(resource)
            if holder and holder in waiters:
                deadlock = Deadlock(
                    deadlock_type="resource_deadlock",
                    involved_agents=[holder] + waiters,
                    description=f"Resource deadlock on '{resource}': "
                                 f"holder '{holder}' is also waiting",
                    details={"resource": resource, "holder": holder, "waiters": waiters},
                )
                self._detected_deadlocks.append(deadlock)
                logger.warning("Resource deadlock detected on '%s'", resource)
                return deadlock.to_dict()
        return None

    def break_deadlock(self, deadlock: Dict[str, Any]) -> Dict[str, Any]:
        """Break a deadlock using the most appropriate strategy."""
        deadlock_type = deadlock.get("deadlock_type", "unknown")
        agents = deadlock.get("involved_agents", [])

        if not agents:
            return {"action": "no_agents", "success": False}

        # Strategy: remove the lowest-priority agent from the cycle
        from resolver.arbitrator import AgentArbitrator  # pylint: disable=import-outside-toplevel
        priorities = AgentArbitrator.DEFAULT_PRIORITIES
        victim = min(agents, key=lambda a: priorities.get(a, 0))

        action = {
            "action": "preempt_agent",
            "victim": victim,
            "deadlock_type": deadlock_type,
            "rationale": f"Agent '{victim}' preempted to break deadlock",
            "success": True,
        }

        # Remove the victim from the wait graph
        self._wait_graph.pop(victim, None)
        for agent_waiters in self._wait_graph.values():
            agent_waiters.discard(victim)

        logger.info("Deadlock broken: preempted agent '%s'", victim)
        return action

    @property
    def detected_deadlocks(self) -> List[Dict[str, Any]]:
        """Return history of all detected deadlocks."""
        return [d.to_dict() for d in self._detected_deadlocks]

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _find_cycle(self) -> Optional[List[str]]:
        """Return the nodes of a cycle in the wait graph, or None if none exists."""
        visited: Set[str] = set()
        path: List[str] = []
        path_set: Set[str] = set()

        def dfs(node: str) -> Optional[List[str]]:
            visited.add(node)
            path.append(node)
            path_set.add(node)
            for neighbour in self._wait_graph.get(node, set()):
                if neighbour not in visited:
                    result = dfs(neighbour)
                    if result is not None:
                        return result
                elif neighbour in path_set:
                    # Found a cycle; extract the cycle portion
                    cycle_start = path.index(neighbour)
                    return path[cycle_start:]
            path.pop()
            path_set.discard(node)
            return None

        for node in list(self._wait_graph.keys()):
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle
        return None
