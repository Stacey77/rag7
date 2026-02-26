"""
Agent arbitration logic for the Resolver Agent.

Decides which agent gets control, which tasks take priority, and how
limited resources are allocated when multiple agents compete.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ArbitrationStrategy(Enum):
    """Available arbitration strategies."""
    PRIORITY_QUEUE = "priority_queue"
    ROUND_ROBIN = "round_robin"
    WEIGHTED_FAIR = "weighted_fair"
    EMERGENCY_OVERRIDE = "emergency_override"
    HUMAN_IN_THE_LOOP = "human_in_the_loop"


@dataclass
class ArbitrationResult:
    """Outcome of an arbitration decision."""
    strategy: ArbitrationStrategy
    winner: Optional[str]
    allocation: Dict[str, Any]
    rationale: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "winner": self.winner,
            "allocation": self.allocation,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
        }


class AgentArbitrator:
    """
    Arbitrate between competing agent requests.

    Default agent priorities (higher number = higher priority):
        resolver      → 6   (highest; can override all)
        perception    → 5
        planning      → 4
        control       → 3
        communication → 2
        coordination  → 1
    """

    DEFAULT_PRIORITIES: Dict[str, int] = {
        "perception": 5,
        "planning": 4,
        "control": 3,
        "communication": 2,
        "coordination": 1,
        "resolver": 6,
    }

    def __init__(self, agent_priorities: Optional[Dict[str, int]] = None):
        self.agent_priorities = agent_priorities or dict(self.DEFAULT_PRIORITIES)
        self._round_robin_index: Dict[str, int] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def arbitrate_control_request(
        self,
        requests: List[Dict[str, Any]],
        strategy: ArbitrationStrategy = ArbitrationStrategy.PRIORITY_QUEUE,
    ) -> Dict[str, Any]:
        """Determine which agent gets control of the robot."""
        if not requests:
            return ArbitrationResult(
                strategy=strategy,
                winner=None,
                allocation={},
                rationale="No requests to arbitrate",
            ).to_dict()

        # Emergency requests always override normal priority
        emergency = [r for r in requests if r.get("emergency", False)]
        if emergency:
            return self._emergency_override(emergency, "control")

        return self._priority_queue_arbitration(requests, "control")

    def arbitrate_resource_allocation(
        self, requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Allocate limited resources (CPU, memory, sensors) among requesting agents."""
        if not requests:
            return ArbitrationResult(
                strategy=ArbitrationStrategy.PRIORITY_QUEUE,
                winner=None,
                allocation={},
                rationale="No resource requests",
            ).to_dict()

        # Group requests by resource
        resource_groups: Dict[str, List[Dict[str, Any]]] = {}
        for req in requests:
            resource = req.get("resource", "unknown")
            resource_groups.setdefault(resource, []).append(req)

        allocation: Dict[str, str] = {}
        for resource, group in resource_groups.items():
            winner = max(group, key=lambda r: self.agent_priorities.get(r.get("agent", ""), 0))
            allocation[resource] = winner.get("agent", "")

        return ArbitrationResult(
            strategy=ArbitrationStrategy.PRIORITY_QUEUE,
            winner=None,
            allocation=allocation,
            rationale="Resources allocated by agent priority",
        ).to_dict()

    def arbitrate_task_priority(
        self, tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine task execution order."""
        if not tasks:
            return ArbitrationResult(
                strategy=ArbitrationStrategy.PRIORITY_QUEUE,
                winner=None,
                allocation={},
                rationale="No tasks to arbitrate",
            ).to_dict()

        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                t.get("priority", 0),
                self.agent_priorities.get(t.get("agent", ""), 0),
            ),
            reverse=True,
        )

        return ArbitrationResult(
            strategy=ArbitrationStrategy.PRIORITY_QUEUE,
            winner=sorted_tasks[0].get("agent"),
            allocation={"ordered_tasks": [t.get("id", str(i))
                                          for i, t in enumerate(sorted_tasks)]},
            rationale="Tasks sorted by priority then agent priority",
        ).to_dict()

    def arbitrate_with_context(
        self, requests: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Context-aware arbitration (e.g., emergency overrides normal priority)."""
        if context.get("emergency"):
            return self._emergency_override(requests, "context_aware")
        return self.arbitrate_control_request(requests)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _priority_queue_arbitration(
        self, requests: List[Dict[str, Any]], resource_type: str
    ) -> Dict[str, Any]:
        winner_req = max(
            requests,
            key=lambda r: (
                r.get("priority", 0),
                self.agent_priorities.get(r.get("agent", ""), 0),
            ),
        )
        winner = winner_req.get("agent", "")
        return ArbitrationResult(
            strategy=ArbitrationStrategy.PRIORITY_QUEUE,
            winner=winner,
            allocation={resource_type: winner},
            rationale=f"Agent '{winner}' selected by priority queue for {resource_type}",
        ).to_dict()

    def _emergency_override(
        self, requests: List[Dict[str, Any]], resource_type: str
    ) -> Dict[str, Any]:
        """Grant control to the highest-priority emergency request."""
        winner_req = max(
            requests,
            key=lambda r: self.agent_priorities.get(r.get("agent", ""), 0),
        )
        winner = winner_req.get("agent", "")
        return ArbitrationResult(
            strategy=ArbitrationStrategy.EMERGENCY_OVERRIDE,
            winner=winner,
            allocation={resource_type: winner},
            rationale=f"Emergency override: '{winner}' granted {resource_type}",
        ).to_dict()

    def _round_robin(
        self, requests: List[Dict[str, Any]], resource_type: str
    ) -> Dict[str, Any]:
        idx = self._round_robin_index.get(resource_type, 0) % len(requests)
        winner = requests[idx].get("agent", "")
        self._round_robin_index[resource_type] = idx + 1
        return ArbitrationResult(
            strategy=ArbitrationStrategy.ROUND_ROBIN,
            winner=winner,
            allocation={resource_type: winner},
            rationale=f"Round-robin selection: index {idx}",
        ).to_dict()
