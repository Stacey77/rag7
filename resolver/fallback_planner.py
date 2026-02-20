"""
Fallback strategy planner for the Resolver Agent.

Provides a hierarchy of fallback strategies when primary approaches fail,
from trying alternative methods all the way to requesting human intervention
or performing a safe shutdown.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


@dataclass
class FallbackPlan:
    """A planned fallback strategy."""
    failure_type: str
    steps: List[Dict[str, Any]]
    depth: int = 0
    requires_human: bool = False
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_type": self.failure_type,
            "steps": self.steps,
            "depth": self.depth,
            "requires_human": self.requires_human,
            "created_at": self.created_at,
        }


@dataclass
class FallbackResult:
    """Outcome of executing a fallback plan."""
    plan: FallbackPlan
    executed_steps: List[str]
    success: bool
    final_action: str
    executed_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_type": self.plan.failure_type,
            "executed_steps": self.executed_steps,
            "success": self.success,
            "final_action": self.final_action,
            "executed_at": self.executed_at,
        }


class FallbackPlanner:
    """
    Plan and execute fallback strategies when primary approaches fail.

    Fallback hierarchy (depth 0 → 3):
    0. Try primary approach
    1. Try alternative method
    2. Request human help
    3. Safe shutdown
    """

    MAX_FALLBACK_DEPTH = 3

    # Maps failure types to ordered lists of fallback step descriptions
    _FALLBACK_TEMPLATES: Dict[str, List[str]] = {
        "navigation": [
            "retry_primary_navigation",
            "try_alternative_path",
            "try_simple_straight_line",
            "try_manual_waypoints",
            "request_human_guidance",
            "stop_safely",
        ],
        "manipulation": [
            "retry_primary_grasp",
            "try_alternative_grasp_approach",
            "try_different_grasp_point",
            "request_human_demonstration",
            "skip_object",
        ],
        "perception": [
            "retry_primary_perception",
            "switch_to_backup_sensor",
            "use_cached_perception_data",
            "request_human_visual_confirmation",
            "degrade_gracefully",
        ],
        "planning": [
            "retry_primary_planner",
            "try_alternative_planner",
            "use_default_safe_plan",
            "request_human_plan",
            "halt_and_wait",
        ],
        "communication": [
            "retry_primary_channel",
            "switch_to_backup_channel",
            "use_cached_commands",
            "request_local_mode",
            "failsafe_autonomous_mode",
        ],
        "generic": [
            "retry_operation",
            "try_safe_alternative",
            "request_human_help",
            "safe_shutdown",
        ],
    }

    def __init__(self):
        self._execution_history: List[FallbackResult] = []

    def plan_fallback(self, failure: Dict[str, Any]) -> FallbackPlan:
        """Create a fallback plan for the given failure."""
        failure_type = failure.get("type", "generic")
        steps_template = self._FALLBACK_TEMPLATES.get(
            failure_type, self._FALLBACK_TEMPLATES["generic"]
        )

        depth = failure.get("depth", 0)
        effective_depth = min(depth, self.MAX_FALLBACK_DEPTH)
        available_steps = steps_template[effective_depth:]

        steps = [
            {"step": i + 1, "action": action, "description": action.replace("_", " ")}
            for i, action in enumerate(available_steps)
        ]

        requires_human = any("human" in s["action"] for s in steps)

        plan = FallbackPlan(
            failure_type=failure_type,
            steps=steps,
            depth=effective_depth,
            requires_human=requires_human,
        )

        logger.info(
            "Fallback plan created for '%s': %d steps (depth=%d)",
            failure_type,
            len(steps),
            effective_depth,
        )
        return plan

    def execute_fallback(self, plan: FallbackPlan) -> Dict[str, Any]:
        """Execute the first viable step in the fallback plan."""
        executed_steps: List[str] = []
        final_action = "none"
        success = False

        for step in plan.steps:
            action = step["action"]
            executed_steps.append(action)
            logger.info("Executing fallback step: %s", action)

            if "human" in action:
                # Cannot automatically execute human-in-the-loop steps
                final_action = f"awaiting_human_for:{action}"
                success = False
                break

            if "shutdown" in action or "stop_safely" in action:
                final_action = action
                success = True
                break

            # Simulate execution success for non-human, non-shutdown steps
            final_action = action
            success = True
            break  # Execute only the first auto-executable step per call

        result = FallbackResult(
            plan=plan,
            executed_steps=executed_steps,
            success=success,
            final_action=final_action,
        )
        self._execution_history.append(result)
        return result.to_dict()

    # Specific fallback helpers referenced in docstrings

    def fallback_navigation(self, depth: int = 0) -> Dict[str, Any]:
        """Execute navigation fallback at the given depth."""
        failure = {"type": "navigation", "depth": depth}
        plan = self.plan_fallback(failure)
        return self.execute_fallback(plan)

    def fallback_manipulation(self, depth: int = 0) -> Dict[str, Any]:
        """Execute manipulation fallback at the given depth."""
        failure = {"type": "manipulation", "depth": depth}
        plan = self.plan_fallback(failure)
        return self.execute_fallback(plan)

    @property
    def execution_history(self) -> List[Dict[str, Any]]:
        """Return all previously executed fallback results."""
        return [r.to_dict() for r in self._execution_history]
