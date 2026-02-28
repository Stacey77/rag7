"""
Planning agent module for the RAG7 AGI Robotics Framework.

Provides high-level task planning, decomposition, and replanning using
LangChain-based LLMs with a rule-based fallback.
"""

import logging
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent

try:
    from langchain.agents import AgentExecutor  # noqa: F401
    from langchain_openai import ChatOpenAI  # noqa: F401

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class PlanningAgent(BaseAgent):
    """Agent responsible for high-level task planning and goal decomposition.

    Uses LangChain with an LLM backend when available; falls back to a
    deterministic rule-based planner otherwise.

    Args:
        config: Agent configuration dictionary.
        llm_config: Optional LLM configuration dictionary.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the planning agent."""
        super().__init__(
            name="planning_agent",
            config=config,
            logger=logging.getLogger("rag7.planning"),
        )
        self._llm_config = llm_config or {}
        self._llm = None
        self._current_plan: List[Dict[str, Any]] = []
        self._plan_index: int = 0
        self._world_state: Dict[str, Any] = {}

        if LANGCHAIN_AVAILABLE and self._llm_config.get("provider") == "openai":
            self._try_init_llm()

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def perceive(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Update the internal world model with new observations.

        Args:
            observation: Dictionary containing world state updates.

        Returns:
            Updated world state.
        """
        self._world_state.update(observation)
        self.update_state("world_state", self._world_state)
        return self._world_state

    def reason(self, context: Any) -> Dict[str, Any]:
        """Create or refine a task plan based on current context.

        Args:
            context: Goal description string or context dictionary.

        Returns:
            Dictionary with ``plan`` (list of step dicts) and
            ``status`` keys.
        """
        goal = context if isinstance(context, str) else context.get("goal", "idle")
        plan = self.create_plan(goal)
        self._current_plan = plan
        self._plan_index = 0
        return {"plan": plan, "status": "planned", "num_steps": len(plan)}

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the next step in the current plan.

        Args:
            action: Action override dict; if ``{"type": "next"}`` is
                provided, advances to the next plan step.

        Returns:
            Dictionary describing which step was executed.
        """
        if not self._current_plan:
            return {"status": "no_plan"}

        if self._plan_index >= len(self._current_plan):
            return {"status": "plan_complete"}

        step = self._current_plan[self._plan_index]
        self._plan_index += 1
        self._logger.info("Executing plan step %d: %s", self._plan_index, step)
        return {"status": "executing", "step": step}

    # ------------------------------------------------------------------
    # Public planning API
    # ------------------------------------------------------------------

    def create_plan(self, goal: str) -> List[Dict[str, Any]]:
        """Create a task plan to achieve the given goal.

        Attempts LLM-based planning if available; falls back to
        rule-based decomposition.

        Args:
            goal: High-level goal description.

        Returns:
            Ordered list of step dictionaries, each containing at least
            ``step_id``, ``action``, and ``description`` keys.
        """
        if self._llm is not None:
            try:
                return self._llm_plan(goal)
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("LLM planning failed (%s); using rule-based.", exc)

        return self._decompose_task(goal)

    def _decompose_task(self, task: str) -> List[Dict[str, Any]]:
        """Decompose a task string into a sequence of primitive steps.

        Args:
            task: Task description string.

        Returns:
            List of step dictionaries.
        """
        task_lower = task.lower()

        if "navigate" in task_lower or "go to" in task_lower or "move" in task_lower:
            return [
                {"step_id": 1, "action": "perceive_environment", "description": "Scan surroundings"},
                {"step_id": 2, "action": "plan_path", "description": "Compute collision-free path"},
                {"step_id": 3, "action": "navigate", "description": "Execute navigation"},
                {"step_id": 4, "action": "verify_position", "description": "Confirm arrival"},
            ]

        if "grasp" in task_lower or "pick" in task_lower or "grab" in task_lower:
            return [
                {"step_id": 1, "action": "detect_object", "description": "Locate target object"},
                {"step_id": 2, "action": "approach", "description": "Move arm above object"},
                {"step_id": 3, "action": "grasp", "description": "Close gripper"},
                {"step_id": 4, "action": "lift", "description": "Lift object"},
            ]

        if "place" in task_lower or "put" in task_lower:
            return [
                {"step_id": 1, "action": "move_to_target", "description": "Move to placement location"},
                {"step_id": 2, "action": "lower", "description": "Lower arm"},
                {"step_id": 3, "action": "release", "description": "Open gripper"},
            ]

        # Generic default plan
        return [
            {"step_id": 1, "action": "assess", "description": f"Assess task: {task}"},
            {"step_id": 2, "action": "execute", "description": "Execute task"},
            {"step_id": 3, "action": "verify", "description": "Verify completion"},
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _llm_plan(self, goal: str) -> List[Dict[str, Any]]:
        """Generate a plan using the LLM backend.

        Args:
            goal: Goal description.

        Returns:
            List of step dictionaries from LLM output.
        """
        prompt = (
            f"Create a step-by-step robot task plan for: {goal}\n"
            "Return steps as a numbered list."
        )
        response = self._llm.invoke(prompt)
        lines = [l.strip() for l in response.content.split("\n") if l.strip()]
        steps = []
        for i, line in enumerate(lines, 1):
            steps.append({"step_id": i, "action": "llm_step", "description": line})
        return steps

    def _try_init_llm(self) -> None:
        """Attempt to initialise the LangChain LLM client."""
        try:
            import os

            from langchain_openai import ChatOpenAI

            api_key = os.environ.get(
                self._llm_config.get("api_key_env", "OPENAI_API_KEY"), ""
            )
            if not api_key:
                self._logger.info("No OpenAI API key found; using rule-based planning.")
                return
            self._llm = ChatOpenAI(
                model=self._llm_config.get("model", "gpt-4"),
                temperature=self._llm_config.get("temperature", 0.1),
                openai_api_key=api_key,
            )
            self._logger.info("LLM planning backend initialised.")
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Failed to initialise LLM: %s", exc)
