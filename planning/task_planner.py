"""
Task planner module for the rag7 planning system.

Decomposes high-level goals into ordered sequences of primitive actions,
using an LLM when available and falling back to rule-based planning.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from langchain_openai import ChatOpenAI  # noqa: F401

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class TaskPlanner:
    """High-level task planner that decomposes goals into sub-tasks.

    When an LLM is configured and reachable it uses chain-of-thought
    prompting to create plans; otherwise a deterministic rule-based
    planner is used.

    Args:
        llm_config: Optional LLM configuration dictionary.
    """

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the task planner."""
        self._logger = logging.getLogger("rag7.planning.task")
        self._llm_config = llm_config or {}
        self._llm = None

        if LANGCHAIN_AVAILABLE and self._llm_config.get("provider") == "openai":
            self._try_init_llm()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan(
        self, goal: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Create a task plan to achieve the specified goal.

        Args:
            goal: High-level goal description string.
            context: Optional world-state context dictionary.

        Returns:
            Ordered list of step dictionaries, each containing
            ``step_id``, ``action``, and ``description`` keys.
        """
        context = context or {}
        if self._llm is not None:
            try:
                return self._llm_plan(goal, context)
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("LLM planning failed: %s; using rule-based.", exc)

        return self.decompose(goal)

    def decompose(self, task: str) -> List[Dict[str, Any]]:
        """Decompose a task string into primitive sub-tasks.

        Args:
            task: Task or goal description.

        Returns:
            List of step dictionaries.
        """
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["navigate", "go", "move", "drive"]):
            return [
                {"step_id": 1, "action": "scan_environment", "description": "Scan for obstacles"},
                {"step_id": 2, "action": "compute_path", "description": "Plan collision-free path"},
                {"step_id": 3, "action": "navigate", "description": "Execute navigation"},
                {"step_id": 4, "action": "confirm_arrival", "description": "Verify goal reached"},
            ]

        if any(kw in task_lower for kw in ["grasp", "pick", "grab", "take"]):
            return [
                {"step_id": 1, "action": "detect_object", "description": "Detect target object"},
                {"step_id": 2, "action": "plan_approach", "description": "Plan approach trajectory"},
                {"step_id": 3, "action": "execute_grasp", "description": "Perform grasp"},
                {"step_id": 4, "action": "verify_grasp", "description": "Check grasp success"},
            ]

        if any(kw in task_lower for kw in ["place", "put", "deposit"]):
            return [
                {"step_id": 1, "action": "find_placement", "description": "Find placement location"},
                {"step_id": 2, "action": "navigate_to_placement", "description": "Move to placement"},
                {"step_id": 3, "action": "lower_object", "description": "Lower arm with object"},
                {"step_id": 4, "action": "release", "description": "Open gripper"},
            ]

        if any(kw in task_lower for kw in ["inspect", "check", "examine"]):
            return [
                {"step_id": 1, "action": "approach_target", "description": "Move near target"},
                {"step_id": 2, "action": "capture_images", "description": "Take inspection images"},
                {"step_id": 3, "action": "analyse", "description": "Analyse inspection data"},
                {"step_id": 4, "action": "report", "description": "Generate inspection report"},
            ]

        # Generic fallback
        return [
            {"step_id": 1, "action": "assess", "description": f"Assess: {task}"},
            {"step_id": 2, "action": "plan", "description": "Create execution plan"},
            {"step_id": 3, "action": "execute", "description": "Execute plan"},
            {"step_id": 4, "action": "verify", "description": "Verify outcome"},
        ]

    def replan(
        self,
        failed_step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate a recovery plan after a step failure.

        Args:
            failed_step: The step dictionary that failed.
            context: Updated world-state context.

        Returns:
            Recovery plan as a list of step dictionaries.
        """
        context = context or {}
        reason = context.get("failure_reason", "unknown")
        self._logger.warning(
            "Replanning after failed step '%s' (reason: %s).",
            failed_step.get("action"),
            reason,
        )
        recovery = [
            {"step_id": 1, "action": "diagnose", "description": f"Diagnose failure: {reason}"},
            {"step_id": 2, "action": "recover", "description": "Execute recovery action"},
        ]
        # Append original remaining steps after recovery
        remaining = context.get("remaining_steps", [])
        for i, step in enumerate(remaining, start=3):
            step = dict(step)
            step["step_id"] = i
            recovery.append(step)
        return recovery

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _llm_plan(
        self, goal: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create a plan using the LLM backend."""
        prompt = (
            f"Robot task: {goal}\nContext: {context}\n"
            "Provide a numbered step-by-step plan for the robot."
        )
        response = self._llm.invoke(prompt)
        lines = [l.strip() for l in response.content.split("\n") if l.strip()]
        return [
            {"step_id": i, "action": "llm_step", "description": line}
            for i, line in enumerate(lines, 1)
        ]

    def _try_init_llm(self) -> None:
        """Attempt to initialise the LangChain LLM client."""
        try:
            import os

            from langchain_openai import ChatOpenAI

            api_key = os.environ.get(
                self._llm_config.get("api_key_env", "OPENAI_API_KEY"), ""
            )
            if not api_key:
                return
            self._llm = ChatOpenAI(
                model=self._llm_config.get("model", "gpt-4"),
                temperature=self._llm_config.get("temperature", 0.1),
                openai_api_key=api_key,
            )
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("TaskPlanner LLM init failed: %s", exc)
