"""
Conflict resolution module for the Resolver Agent.

Provides:
- ConflictDetector  – detect conflicts between agents
- ConflictResolver  – apply resolution strategies
- ConflictPredictor – rule-based conflict prediction (ML version in predictor.py)
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Enumeration of recognised conflict categories."""
    PERCEPTION_PLANNING = "perception_planning"
    CONTROL = "control"
    TASK = "task"
    RESOURCE = "resource"
    COMMUNICATION = "communication"
    UNKNOWN = "unknown"


class ResolutionStrategy(Enum):
    """Enumeration of available resolution strategies."""
    PRIORITY_BASED = "priority_based"
    VOTING = "voting"
    EXPERTISE = "expertise"
    TIME_BASED = "time_based"
    COST_BASED = "cost_based"
    ML_BASED = "ml_based"


@dataclass
class Conflict:
    """Data class describing a detected conflict."""
    conflict_type: ConflictType
    agents: List[str]
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    severity: int = 1
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.conflict_type.value,
            "agents": self.agents,
            "description": self.description,
            "details": self.details,
            "severity": self.severity,
            "timestamp": self.timestamp,
        }


@dataclass
class Resolution:
    """Data class describing the outcome of a conflict resolution."""
    strategy: ResolutionStrategy
    winning_agent: Optional[str]
    action: str
    rationale: str
    success: bool = True
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "winning_agent": self.winning_agent,
            "action": self.action,
            "rationale": self.rationale,
            "success": self.success,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# ConflictDetector
# ---------------------------------------------------------------------------

class ConflictDetector:
    """
    Detect conflicts between agents.

    Supports detection of:
    - Perception vs Planning disagreements
    - Competing control commands
    - Overlapping or contradictory tasks
    - Resource contention
    """

    def detect_all(self, agent_states: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run all detectors and return a list of detected conflicts."""
        conflicts: List[Dict[str, Any]] = []
        conflicts.extend(self.detect_perception_planning_conflict(agent_states))
        conflicts.extend(self.detect_control_conflict(agent_states))
        conflicts.extend(self.detect_task_conflict(agent_states))
        conflicts.extend(self.detect_resource_conflict(agent_states))
        return conflicts

    def detect_perception_planning_conflict(
        self, agent_states: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between Perception and Planning agents."""
        conflicts: List[Dict[str, Any]] = []
        perception = agent_states.get("perception")
        planning = agent_states.get("planning")

        if perception and planning:
            perception_meta = getattr(perception, "metadata", {})
            planning_meta = getattr(planning, "metadata", {})
            p_objects = set(perception_meta.get("detected_objects", []))
            pl_objects = set(planning_meta.get("known_objects", []))
            disagreements = p_objects.symmetric_difference(pl_objects)

            if disagreements:
                conflict = Conflict(
                    conflict_type=ConflictType.PERCEPTION_PLANNING,
                    agents=["perception", "planning"],
                    description="Object detection disagreement between Perception and Planning",
                    details={
                        "perception_objects": list(p_objects),
                        "planning_objects": list(pl_objects),
                        "disagreements": list(disagreements),
                    },
                    severity=2,
                )
                conflicts.append(conflict.to_dict())
        return conflicts

    def detect_control_conflict(self, agent_states: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts where multiple agents compete for robot control."""
        conflicts: List[Dict[str, Any]] = []
        control_requesting = [
            name for name, state in agent_states.items()
            if getattr(state, "metadata", {}).get("requesting_control", False)
        ]

        if len(control_requesting) > 1:
            conflict = Conflict(
                conflict_type=ConflictType.CONTROL,
                agents=control_requesting,
                description="Multiple agents requesting simultaneous robot control",
                details={"requesters": control_requesting},
                severity=3,
            )
            conflicts.append(conflict.to_dict())
        return conflicts

    def detect_task_conflict(self, agent_states: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect overlapping or contradictory task assignments."""
        conflicts: List[Dict[str, Any]] = []
        task_assignments: Dict[str, List[str]] = {}

        for agent_name, state in agent_states.items():
            tasks = getattr(state, "metadata", {}).get("assigned_tasks", [])
            for task_id in tasks:
                task_assignments.setdefault(task_id, []).append(agent_name)

        for task_id, agents in task_assignments.items():
            if len(agents) > 1:
                conflict = Conflict(
                    conflict_type=ConflictType.TASK,
                    agents=agents,
                    description=f"Task '{task_id}' assigned to multiple agents",
                    details={"task_id": task_id, "assigned_agents": agents},
                    severity=2,
                )
                conflicts.append(conflict.to_dict())
        return conflicts

    def detect_resource_conflict(self, agent_states: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect when multiple agents compete for the same resource."""
        conflicts: List[Dict[str, Any]] = []
        resource_requests: Dict[str, List[str]] = {}

        for agent_name, state in agent_states.items():
            resources = getattr(state, "metadata", {}).get("requested_resources", [])
            for resource in resources:
                resource_requests.setdefault(resource, []).append(agent_name)

        for resource, agents in resource_requests.items():
            if len(agents) > 1:
                conflict = Conflict(
                    conflict_type=ConflictType.RESOURCE,
                    agents=agents,
                    description=f"Resource '{resource}' requested by multiple agents",
                    details={"resource": resource, "requesting_agents": agents},
                    severity=2,
                )
                conflicts.append(conflict.to_dict())
        return conflicts


# ---------------------------------------------------------------------------
# ConflictResolver
# ---------------------------------------------------------------------------

# Default agent priorities used for priority-based resolution
_DEFAULT_PRIORITIES: Dict[str, int] = {
    "perception": 5,
    "planning": 4,
    "control": 3,
    "communication": 2,
    "coordination": 1,
    "resolver": 6,
}


class ConflictResolver:
    """
    Apply resolution strategies to detected conflicts.

    Available strategies:
    1. Priority-based (higher priority wins)
    2. Voting (majority rules)
    3. Expert arbitration (most qualified agent decides)
    4. Time-based (first-come-first-served)
    5. Cost-based (least cost approach)
    6. ML-based (learned from past resolutions)
    """

    def __init__(self, agent_priorities: Optional[Dict[str, int]] = None):
        self._priorities = agent_priorities or _DEFAULT_PRIORITIES
        self._resolution_history: List[Dict[str, Any]] = []

    def resolve(self, conflict: Dict[str, Any],
                strategy: ResolutionStrategy = ResolutionStrategy.PRIORITY_BASED
                ) -> Dict[str, Any]:
        """Resolve a conflict using the specified strategy."""
        strategy_map = {
            ResolutionStrategy.PRIORITY_BASED: self.resolve_by_priority,
            ResolutionStrategy.VOTING: self.resolve_by_voting,
            ResolutionStrategy.EXPERTISE: self.resolve_by_expertise,
            ResolutionStrategy.COST_BASED: self.resolve_by_cost,
            ResolutionStrategy.ML_BASED: self.resolve_by_ml,
        }
        handler = strategy_map.get(strategy, self.resolve_by_priority)
        resolution = handler(conflict)
        self._resolution_history.append(resolution.to_dict())
        logger.info("Conflict resolved via %s: %s", strategy.value, resolution.action)
        return resolution.to_dict()

    def resolve_by_priority(self, conflict: Dict[str, Any]) -> Resolution:
        """Resolve by selecting the highest-priority agent."""
        agents = conflict.get("agents", [])
        if not agents:
            return Resolution(
                strategy=ResolutionStrategy.PRIORITY_BASED,
                winning_agent=None,
                action="no_agents_involved",
                rationale="No agents listed in conflict",
                success=False,
            )
        winner = max(agents, key=lambda a: self._priorities.get(a, 0))
        return Resolution(
            strategy=ResolutionStrategy.PRIORITY_BASED,
            winning_agent=winner,
            action=f"grant_control_to_{winner}",
            rationale=f"Agent '{winner}' has highest priority "
                       f"({self._priorities.get(winner, 0)})",
        )

    def resolve_by_voting(self, conflict: Dict[str, Any]) -> Resolution:
        """Resolve by majority vote among connected agents (simplified simulation)."""
        agents = conflict.get("agents", [])
        # In a real system this would broadcast a vote request; here we use priorities
        votes: Dict[str, int] = {a: self._priorities.get(a, 0) for a in agents}
        if not votes:
            return Resolution(
                strategy=ResolutionStrategy.VOTING,
                winning_agent=None,
                action="no_votes",
                rationale="No agents to vote",
                success=False,
            )
        winner = max(votes, key=lambda a: votes[a])
        return Resolution(
            strategy=ResolutionStrategy.VOTING,
            winning_agent=winner,
            action=f"grant_control_to_{winner}",
            rationale=f"Agent '{winner}' received highest weighted vote ({votes[winner]})",
        )

    def resolve_by_expertise(self, conflict: Dict[str, Any]) -> Resolution:
        """Resolve by selecting the most domain-relevant agent."""
        conflict_type = conflict.get("type", ConflictType.UNKNOWN.value)
        expertise_map: Dict[str, str] = {
            ConflictType.PERCEPTION_PLANNING.value: "perception",
            ConflictType.CONTROL.value: "control",
            ConflictType.TASK.value: "coordination",
            ConflictType.RESOURCE.value: "resolver",
        }
        expert = expertise_map.get(conflict_type, "resolver")
        return Resolution(
            strategy=ResolutionStrategy.EXPERTISE,
            winning_agent=expert,
            action=f"delegate_decision_to_{expert}",
            rationale=f"Agent '{expert}' has domain expertise for conflict type '{conflict_type}'",
        )

    def resolve_by_cost(self, conflict: Dict[str, Any]) -> Resolution:
        """Resolve by selecting the lowest-cost option from conflict details."""
        options = conflict.get("details", {}).get("options", [])
        if not options:
            return self.resolve_by_priority(conflict)

        best = min(options, key=lambda o: o.get("cost", float("inf")))
        return Resolution(
            strategy=ResolutionStrategy.COST_BASED,
            winning_agent=best.get("agent"),
            action=f"select_option_{best.get('id', 'best')}",
            rationale=f"Option has minimum cost: {best.get('cost')}",
        )

    def resolve_by_ml(self, conflict: Dict[str, Any]) -> Resolution:
        """Resolve using a trained ML model (falls back to priority-based if unavailable)."""
        try:
            from resolver.predictor import ConflictPredictor  # pylint: disable=import-outside-toplevel
            predictor = ConflictPredictor()
            prediction = predictor.predict_best_resolution(conflict)
            return Resolution(
                strategy=ResolutionStrategy.ML_BASED,
                winning_agent=prediction.get("winning_agent"),
                action=prediction.get("action", "ml_resolution"),
                rationale="ML model prediction",
            )
        except Exception:  # pylint: disable=broad-except
            logger.warning("ML resolution unavailable, falling back to priority-based")
            return self.resolve_by_priority(conflict)

    @property
    def resolution_history(self) -> List[Dict[str, Any]]:
        """Return the full history of resolutions applied."""
        return list(self._resolution_history)


# ---------------------------------------------------------------------------
# ConflictPredictor (rule-based; ML version is in predictor.py)
# ---------------------------------------------------------------------------

class ConflictPredictor:
    """
    Rule-based conflict predictor.

    Analyses current agent states and identifies patterns that historically
    precede conflicts so that preventive actions can be taken.
    """

    def predict(self, agent_states: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return a list of predicted conflicts with prevention suggestions."""
        predictions: List[Dict[str, Any]] = []

        # Rule: If multiple agents are requesting the same resource, a conflict is imminent
        resource_counts: Dict[str, int] = {}
        for state in agent_states.values():
            for resource in getattr(state, "metadata", {}).get("requested_resources", []):
                resource_counts[resource] = resource_counts.get(resource, 0) + 1

        for resource, count in resource_counts.items():
            if count > 1:
                predictions.append({
                    "type": ConflictType.RESOURCE.value,
                    "probability": min(0.5 + count * 0.1, 0.99),
                    "description": f"Resource '{resource}' contention likely",
                    "prevention": f"Pre-allocate '{resource}' before conflict occurs",
                })

        return predictions

    def suggest_preventive_actions(self, agent_states: Dict[str, Any]) -> List[str]:
        """Return a list of preventive action strings."""
        predictions = self.predict(agent_states)
        return [p["prevention"] for p in predictions]
