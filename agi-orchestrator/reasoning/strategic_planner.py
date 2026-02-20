"""Strategic Planner – long-term strategy creation, evaluation, and adaptation.

Plans are represented as ordered sequences of milestones with associated
success criteria, enabling the AGI to reason over multi-step horizons.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


class PlanStatus(Enum):
    """Lifecycle status of a strategic plan."""

    DRAFT = auto()
    ACTIVE = auto()
    ADAPTED = auto()
    COMPLETED = auto()
    ABANDONED = auto()


@dataclass
class Milestone:
    """A single step within a strategic plan.

    Attributes:
        name: Short label for this milestone.
        success_criteria: Dict describing measurable success conditions.
        completed: Whether the milestone has been achieved.
    """

    name: str
    success_criteria: dict[str, Any] = field(default_factory=dict)
    completed: bool = False


@dataclass
class Plan:
    """A long-term strategic plan composed of ordered milestones.

    Attributes:
        plan_id: Unique identifier, auto-generated when omitted.
        objective: High-level goal this plan works toward.
        milestones: Ordered list of :class:`Milestone` steps.
        status: Current lifecycle status.
        score: Evaluation score in ``[0.0, 1.0]`` (higher = better).
        metadata: Arbitrary supporting data.
    """

    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective: str = ""
    milestones: list[Milestone] = field(default_factory=list)
    status: PlanStatus = field(default=PlanStatus.DRAFT)
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class StrategicPlanner:
    """Long-term strategy builder with evaluation and adaptive refinement.

    Attributes:
        _plans: Registry of all created plans keyed by ``plan_id``.
    """

    def __init__(self) -> None:
        """Initialise with an empty plan registry."""
        self._plans: dict[str, Plan] = {}
        log.info("StrategicPlanner initialised")

    def create_plan(
        self,
        objective: str,
        milestones: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Plan:
        """Create and register a new strategic plan.

        Args:
            objective: High-level goal description.
            milestones: Optional list of milestone dicts with at least a
                ``name`` key and an optional ``success_criteria`` mapping.
            metadata: Arbitrary data to attach to the plan.

        Returns:
            The newly created :class:`Plan`.

        Raises:
            ValueError: If *objective* is empty.
        """
        if not objective:
            raise ValueError("objective must not be empty")

        steps: list[Milestone] = []
        for m in milestones or []:
            steps.append(
                Milestone(
                    name=m.get("name", "unnamed"),
                    success_criteria=m.get("success_criteria", {}),
                )
            )

        plan = Plan(
            objective=objective,
            milestones=steps,
            status=PlanStatus.ACTIVE,
            metadata=metadata or {},
        )
        self._plans[plan.plan_id] = plan
        log.info("Plan created", plan_id=plan.plan_id, objective=objective, steps=len(steps))
        return plan

    def evaluate_plan(self, plan_id: str) -> dict[str, Any]:
        """Score an existing plan based on milestone completion rate.

        Args:
            plan_id: Identifier of the plan to evaluate.

        Returns:
            Dict with ``plan_id``, ``objective``, ``score``,
            ``completed_milestones``, ``total_milestones``, and ``status``.

        Raises:
            KeyError: If *plan_id* is not found.
        """
        if plan_id not in self._plans:
            raise KeyError(f"Plan '{plan_id}' not found")

        plan = self._plans[plan_id]
        total = len(plan.milestones)
        completed = sum(1 for m in plan.milestones if m.completed)
        plan.score = completed / total if total else 0.0

        if plan.score >= 1.0:
            plan.status = PlanStatus.COMPLETED

        report = {
            "plan_id": plan.plan_id,
            "objective": plan.objective,
            "score": plan.score,
            "completed_milestones": completed,
            "total_milestones": total,
            "status": plan.status.name,
        }
        log.info("Plan evaluated", **report)
        return report

    def adapt_plan(
        self,
        plan_id: str,
        new_milestones: list[dict[str, Any]] | None = None,
        metadata_updates: dict[str, Any] | None = None,
    ) -> Plan:
        """Refine an existing plan by appending milestones or updating metadata.

        Args:
            plan_id: Identifier of the plan to adapt.
            new_milestones: Additional milestone dicts to append.
            metadata_updates: Key-value pairs merged into the plan's metadata.

        Returns:
            The updated :class:`Plan`.

        Raises:
            KeyError: If *plan_id* is not found.
        """
        if plan_id not in self._plans:
            raise KeyError(f"Plan '{plan_id}' not found")

        plan = self._plans[plan_id]
        for m in new_milestones or []:
            plan.milestones.append(
                Milestone(
                    name=m.get("name", "unnamed"),
                    success_criteria=m.get("success_criteria", {}),
                )
            )
        plan.metadata.update(metadata_updates or {})
        plan.status = PlanStatus.ADAPTED
        log.info(
            "Plan adapted",
            plan_id=plan_id,
            added_milestones=len(new_milestones or []),
        )
        return plan
