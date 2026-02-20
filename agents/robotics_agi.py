"""
Main RoboticsAGI orchestrator for the rag7 AGI Robotics Framework.

Integrates all agents into a unified system capable of executing
natural language commands and complex multi-step robotic tasks.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import yaml

from agents.base_agent import BaseAgent
from agents.communication_agent import CommunicationAgent
from agents.control_agent import ControlAgent
from agents.coordination_agent import CoordinationAgent
from agents.perception_agent import PerceptionAgent
from agents.planning_agent import PlanningAgent


class RoboticsAGI:
    """Top-level orchestrator for the rag7 AGI robotics system.

    Composes all specialised agents and exposes a high-level API for
    natural language command execution and task management.

    Args:
        ros2_interface: Optional ROS2 interface instance.
        llm_provider: LLM provider string (e.g. ``"openai"``).
        enable_learning: Enable reinforcement-learning components.
        config_path: Path to the directory containing YAML config files.
    """

    def __init__(
        self,
        ros2_interface: Optional[Any] = None,
        llm_provider: str = "openai",
        enable_learning: bool = False,
        config_path: str = "config",
    ) -> None:
        """Initialize the RoboticsAGI system."""
        self._logger = logging.getLogger("rag7.agi")
        self._ros2_interface = ros2_interface
        self._enable_learning = enable_learning

        # Load configurations
        self._agent_config = self._load_yaml(
            os.path.join(config_path, "agent_config.yaml")
        )
        self._llm_config = self._load_yaml(
            os.path.join(config_path, "llm_config.yaml")
        )
        self._robot_config = self._load_yaml(
            os.path.join(config_path, "robot_config.yaml")
        )

        # Override provider if specified
        if llm_provider:
            self._llm_config["provider"] = llm_provider

        # Initialise agents
        self._perception = PerceptionAgent(
            config=self._agent_config.get("perception_agent", {})
        )
        self._planning = PlanningAgent(
            config=self._agent_config.get("planning_agent", {}),
            llm_config=self._llm_config,
        )
        self._control = ControlAgent(
            config=self._agent_config.get("control_agent", {}),
            ros2_enabled=(ros2_interface is not None),
        )
        self._communication = CommunicationAgent(
            config=self._agent_config.get("communication_agent", {}),
            llm_config=self._llm_config,
        )
        self._coordination = CoordinationAgent(
            config=self._agent_config.get("coordination_agent", {})
        )

        # Register all agents with the coordinator
        for agent in [
            self._perception,
            self._planning,
            self._control,
            self._communication,
        ]:
            self._coordination.register_agent(agent)

        self._logger.info("RoboticsAGI system initialised.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_command(self, text: str) -> Dict[str, Any]:
        """Parse and execute a natural language command.

        Args:
            text: Natural language command string from the operator.

        Returns:
            Execution result dictionary with ``success``, ``intent``,
            and ``result`` keys.
        """
        parsed = self._communication.parse_command(text)
        intent = parsed.get("intent", "unknown")
        self._logger.info("Executing command: '%s' (intent=%s)", text, intent)

        task = self.create_task(
            task_type=intent,
            location=parsed.get("location"),
            target_object=parsed.get("target_object"),
        )
        result = self.execute_task(task)
        response = self._communication.generate_response(
            {"intent": intent, "robot_state": self.get_status()}
        )
        return {
            "success": result.get("success", False),
            "intent": intent,
            "result": result,
            "response": response,
        }

    def create_task(self, task_type: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a structured task dictionary.

        Args:
            task_type: Type of task (e.g. ``"navigate"``, ``"grasp"``).
            **kwargs: Additional task parameters (e.g. ``location``,
                ``target_object``).

        Returns:
            Task specification dictionary.
        """
        import time

        return {
            "task_id": f"{task_type}_{int(time.time())}",
            "task_type": task_type,
            **kwargs,
        }

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a structured task using the appropriate agents.

        Args:
            task: Task specification dictionary.

        Returns:
            Result dictionary with ``success`` and ``details`` keys.
        """
        task_type = task.get("task_type", "unknown")

        if task_type == "navigate":
            location = task.get("location") or {}
            x = float(location.get("x", 0.0)) if isinstance(location, dict) else 0.0
            y = float(location.get("y", 0.0)) if isinstance(location, dict) else 0.0
            success = self._control.navigate_to(x, y, 0.0)
            return {"success": success, "details": f"Navigated to ({x}, {y})"}

        if task_type == "grasp":
            obj = task.get("target_object", "unknown")
            success = self._control.execute_grasp(obj)
            return {"success": success, "details": f"Grasped '{obj}'"}

        if task_type == "stop":
            self._control.emergency_stop()
            return {"success": True, "details": "Emergency stop executed"}

        if task_type in ("query", "unknown"):
            status = self.get_status()
            return {"success": True, "details": status}

        # For complex tasks, use planning agent
        plan_result = self._planning.reason({"goal": str(task)})
        return {
            "success": True,
            "details": f"Plan created with {plan_result.get('num_steps', 0)} steps",
            "plan": plan_result.get("plan", []),
        }

    def coordinate_robots(
        self, robots: List[Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate multiple robots to execute a task.

        Args:
            robots: List of robot agent instances.
            task: Task specification dictionary.

        Returns:
            Coordination result dictionary.
        """
        for robot in robots:
            if isinstance(robot, BaseAgent):
                try:
                    self._coordination.register_agent(robot)
                except ValueError:
                    pass  # Already at capacity or already registered
        return self._coordination.coordinate([task])

    def get_status(self) -> Dict[str, Any]:
        """Return a comprehensive system status snapshot.

        Returns:
            Dictionary with per-agent status and system-level flags.
        """
        return {
            "system": "online",
            "perception": self._perception.state,
            "planning": self._planning.state,
            "control": self._control.state,
            "communication": self._communication.state,
            "coordination": self._coordination.get_agent_status(),
            "robot_config": self._robot_config.get("robot_name", "unknown"),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_yaml(path: str) -> Dict[str, Any]:
        """Load a YAML configuration file.

        Args:
            path: Path to the YAML file.

        Returns:
            Parsed configuration dictionary, or empty dict on failure.
        """
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
        except FileNotFoundError:
            logging.getLogger("rag7.agi").warning(
                "Config file not found: %s", path
            )
            return {}
        except yaml.YAMLError as exc:
            logging.getLogger("rag7.agi").error(
                "Failed to parse config file '%s': %s", path, exc
            )
            return {}
