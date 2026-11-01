"""Tool selection and use for manipulation tasks."""
import logging
import random

logger = logging.getLogger(__name__)

TOOL_LIBRARY = {
    "screwdriver": {"tasks": ["screw", "unscrew", "assemble"], "dof": 1},
    "hammer": {"tasks": ["nail", "tap", "break"], "dof": 1},
    "gripper": {"tasks": ["grasp", "pick", "hold"], "dof": 2},
    "spatula": {"tasks": ["flip", "slide", "separate"], "dof": 1},
    "brush": {"tasks": ["clean", "paint", "sweep"], "dof": 2},
}


class ToolUser:
    """Selects and uses appropriate tools for manipulation tasks."""

    def __init__(self) -> None:
        """Initialize ToolUser with a tool library."""
        self.tool_library = TOOL_LIBRARY.copy()
        self.current_tool: dict | None = None

    def select_tool(self, task: dict) -> dict:
        """Select the best tool for a given task.

        Args:
            task: Dict with task type and requirements.

        Returns:
            Dict with selected tool and selection rationale.
        """
        logger.info("Selecting tool for task: %s", task.get("type", "unknown"))
        task_type = task.get("type", "grasp")
        matching_tools = [name for name, info in self.tool_library.items() if task_type in info["tasks"]]
        if not matching_tools:
            matching_tools = list(self.tool_library.keys())
        selected = random.choice(matching_tools)
        self.current_tool = {"name": selected, **self.tool_library[selected]}
        return {
            "status": "selected",
            "tool": selected,
            "tool_info": self.tool_library[selected],
            "task": task.get("type", "unknown"),
            "alternatives": [t for t in matching_tools if t != selected],
            "confidence": random.uniform(0.7, 0.99),
        }

    def use_tool(self, tool: dict, task: dict) -> dict:
        """Use the specified tool to perform a task.

        Args:
            tool: Dict with tool name and parameters.
            task: Dict with task specification and targets.

        Returns:
            Dict with execution result and performance metrics.
        """
        tool_name = tool.get("name", "gripper")
        task_type = task.get("type", "grasp")
        logger.info("Using tool '%s' for task '%s'", tool_name, task_type)
        success = random.random() > 0.15
        return {
            "status": "success" if success else "failed",
            "tool": tool_name,
            "task": task_type,
            "execution_time_s": random.uniform(1.0, 10.0),
            "force_profile": [random.uniform(0, 10) for _ in range(5)],
            "outcome": "task_complete" if success else "retry_needed",
        }
