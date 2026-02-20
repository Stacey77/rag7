"""Goal Hierarchy – multi-objective optimisation with priority-queue storage.

Goals are stored as a min-heap keyed on *priority* (lower value = higher
urgency) so that the highest-priority goal is always retrieved first.
"""

from __future__ import annotations

import heapq
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


class GoalStatus(Enum):
    """Lifecycle status of a goal."""

    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    FAILED = auto()
    SUSPENDED = auto()


@dataclass(order=True)
class Goal:
    """A single objective tracked by the hierarchy.

    The dataclass is *ordered* so that :mod:`heapq` can sort goals by
    ``priority`` without a custom key function.

    Attributes:
        priority: Numeric urgency (lower = more urgent).
        name: Short human-readable label.
        description: Extended description of the objective.
        goal_id: Unique identifier, auto-generated when omitted.
        status: Current lifecycle status.
        progress: Completion fraction in ``[0.0, 1.0]``.
        metadata: Arbitrary supporting data.
    """

    priority: float
    name: str = field(compare=False)
    description: str = field(compare=False, default="")
    goal_id: str = field(compare=False, default_factory=lambda: str(uuid.uuid4()))
    status: GoalStatus = field(compare=False, default=GoalStatus.PENDING)
    progress: float = field(compare=False, default=0.0)
    metadata: dict[str, Any] = field(compare=False, default_factory=dict)


class GoalHierarchy:
    """Multi-objective goal store backed by a min-heap priority queue.

    Attributes:
        _heap: Min-heap of :class:`Goal` objects.
        _goals_by_id: Fast O(1) lookup by ``goal_id``.
    """

    def __init__(self) -> None:
        """Initialise an empty goal hierarchy."""
        self._heap: list[Goal] = []
        self._goals_by_id: dict[str, Goal] = {}
        log.info("GoalHierarchy initialised")

    def add_goal(self, goal: Goal) -> str:
        """Add a new goal to the hierarchy.

        Args:
            goal: The :class:`Goal` to register.

        Returns:
            The ``goal_id`` of the newly added goal.

        Raises:
            ValueError: If a goal with the same ``goal_id`` already exists.
        """
        if goal.goal_id in self._goals_by_id:
            raise ValueError(f"Goal '{goal.goal_id}' already exists")
        goal.status = GoalStatus.ACTIVE
        heapq.heappush(self._heap, goal)
        self._goals_by_id[goal.goal_id] = goal
        log.info("Goal added", goal_id=goal.goal_id, name=goal.name, priority=goal.priority)
        return goal.goal_id

    def get_active_goals(self, limit: int | None = None) -> list[Goal]:
        """Return active goals ordered from highest to lowest urgency.

        Args:
            limit: Maximum number of goals to return. Returns all when *None*.

        Returns:
            Sorted list of goals whose status is :attr:`GoalStatus.ACTIVE`.
        """
        active = sorted(
            (g for g in self._goals_by_id.values() if g.status == GoalStatus.ACTIVE),
        )
        result = active[:limit] if limit is not None else active
        log.debug("Active goals retrieved", count=len(result))
        return result

    def evaluate_progress(self, goal_id: str) -> dict[str, Any]:
        """Compute and return a progress snapshot for the requested goal.

        Args:
            goal_id: Identifier of the goal to evaluate.

        Returns:
            A dict with keys ``goal_id``, ``name``, ``status``, ``progress``,
            and ``on_track`` (``True`` when progress > 0.5).

        Raises:
            KeyError: If *goal_id* does not exist in the hierarchy.
        """
        if goal_id not in self._goals_by_id:
            raise KeyError(f"Goal '{goal_id}' not found")
        goal = self._goals_by_id[goal_id]
        report = {
            "goal_id": goal.goal_id,
            "name": goal.name,
            "status": goal.status.name,
            "progress": goal.progress,
            "on_track": goal.progress >= 0.5,
        }
        log.debug("Goal progress evaluated", **report)
        return report

    def update_progress(self, goal_id: str, progress: float) -> None:
        """Update the progress fraction for an existing goal.

        Args:
            goal_id: Identifier of the goal to update.
            progress: New progress value, clamped to ``[0.0, 1.0]``.

        Raises:
            KeyError: If *goal_id* does not exist.
        """
        if goal_id not in self._goals_by_id:
            raise KeyError(f"Goal '{goal_id}' not found")
        goal = self._goals_by_id[goal_id]
        goal.progress = max(0.0, min(1.0, progress))
        if goal.progress >= 1.0:
            goal.status = GoalStatus.COMPLETED
            log.info("Goal completed", goal_id=goal_id)
        else:
            log.debug("Goal progress updated", goal_id=goal_id, progress=goal.progress)
