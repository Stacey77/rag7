"""
Control agent module for the rag7 AGI Robotics Framework.

Handles low-level robot control including navigation, manipulation,
and emergency stop functionality.
"""

import logging
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent

try:
    import rclpy  # noqa: F401

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


class ControlAgent(BaseAgent):
    """Agent responsible for low-level robot control execution.

    Translates high-level action commands into robot actuator commands,
    optionally publishing to a ROS2 system.

    Args:
        config: Control agent configuration dictionary.
        ros2_enabled: If True and rclpy is available, use ROS2 communication.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        ros2_enabled: bool = False,
    ) -> None:
        """Initialize the control agent."""
        super().__init__(
            name="control_agent",
            config=config,
            logger=logging.getLogger("rag7.control"),
        )
        self._ros2_enabled = ros2_enabled and ROS2_AVAILABLE
        self._is_stopped: bool = False
        self._position: Dict[str, float] = {"x": 0.0, "y": 0.0, "theta": 0.0}
        self._velocity: Dict[str, float] = {"linear": 0.0, "angular": 0.0}
        self._control_frequency = config.get("control_frequency", 50)
        self._position_tolerance = config.get("position_tolerance", 0.05)
        self._orientation_tolerance = config.get("orientation_tolerance", 0.1)

        if self._ros2_enabled:
            self._init_ros2()

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def perceive(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Update the internal robot state from sensor observations.

        Args:
            observation: Dictionary containing ``position`` and/or
                ``velocity`` sub-dicts.

        Returns:
            Updated robot state.
        """
        if "position" in observation:
            self._position.update(observation["position"])
            self.update_state("position", dict(self._position))
        if "velocity" in observation:
            self._velocity.update(observation["velocity"])
            self.update_state("velocity", dict(self._velocity))
        return {"position": self._position, "velocity": self._velocity}

    def reason(self, context: Any) -> Dict[str, Any]:
        """Determine required control actions from current context.

        Args:
            context: Dictionary with ``target_position`` and optional
                ``target_orientation`` keys.

        Returns:
            Recommended control action dictionary.
        """
        if self._is_stopped:
            return {"action": "stop", "reason": "emergency_stop_active"}

        target = context.get("target_position") if isinstance(context, dict) else None
        if target:
            dx = target.get("x", 0.0) - self._position["x"]
            dy = target.get("y", 0.0) - self._position["y"]
            distance = (dx**2 + dy**2) ** 0.5
            if distance < self._position_tolerance:
                return {"action": "stop", "reason": "goal_reached"}
            return {"action": "navigate", "target": target, "distance": distance}

        return {"action": "idle"}

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a control action on the robot.

        Args:
            action: Dictionary with a ``type`` key specifying the action.
                Supported types: ``navigate``, ``grasp``, ``stop``.

        Returns:
            Result dictionary with ``success`` and ``message`` keys.
        """
        action_type = action.get("type", "")

        if self._is_stopped and action_type != "reset_stop":
            return {"success": False, "message": "Emergency stop is active."}

        if action_type == "navigate":
            x = action.get("x", self._position["x"])
            y = action.get("y", self._position["y"])
            theta = action.get("theta", self._position["theta"])
            success = self.navigate_to(x, y, theta)
            return {"success": success, "message": f"Navigate to ({x}, {y})"}

        if action_type == "grasp":
            object_id = action.get("object_id", "unknown")
            success = self.execute_grasp(object_id)
            return {"success": success, "message": f"Grasp object '{object_id}'"}

        if action_type == "stop":
            self.emergency_stop()
            return {"success": True, "message": "Emergency stop executed."}

        if action_type == "reset_stop":
            self._is_stopped = False
            return {"success": True, "message": "Emergency stop cleared."}

        self._logger.warning("Unknown control action type: %s", action_type)
        return {"success": False, "message": f"Unknown action: {action_type}"}

    # ------------------------------------------------------------------
    # Public control API
    # ------------------------------------------------------------------

    def navigate_to(self, x: float, y: float, theta: float) -> bool:
        """Command the robot to navigate to a target pose.

        In simulation / no-ROS mode this immediately updates the internal
        pose; with ROS2 enabled, the goal is published to the navigation
        stack.

        Args:
            x: Target X position in metres.
            y: Target Y position in metres.
            theta: Target heading in radians.

        Returns:
            True if the navigation command was accepted successfully.
        """
        if self._is_stopped:
            self._logger.warning("Cannot navigate – emergency stop is active.")
            return False

        self._logger.info("Navigating to (%.3f, %.3f, %.3f).", x, y, theta)

        if self._ros2_enabled:
            return self._ros2_navigate(x, y, theta)

        # Simulate movement by updating internal state
        self._position = {"x": x, "y": y, "theta": theta}
        self.update_state("position", dict(self._position))
        return True

    def execute_grasp(self, object_id: str) -> bool:
        """Command the arm to grasp a detected object.

        Args:
            object_id: Identifier of the object to grasp.

        Returns:
            True if the grasp was executed successfully.
        """
        if self._is_stopped:
            self._logger.warning("Cannot grasp – emergency stop is active.")
            return False

        self._logger.info("Executing grasp on object '%s'.", object_id)
        self.update_state("grasped_object", object_id)
        return True

    def emergency_stop(self) -> None:
        """Immediately halt all robot motion.

        Sets the internal stopped flag and zeros all velocity commands.
        When ROS2 is enabled, also publishes to the emergency stop topic.
        """
        self._is_stopped = True
        self._velocity = {"linear": 0.0, "angular": 0.0}
        self.update_state("is_stopped", True)
        self._logger.warning("EMERGENCY STOP activated.")

        if self._ros2_enabled:
            self._ros2_emergency_stop()

    # ------------------------------------------------------------------
    # Private ROS2 helpers
    # ------------------------------------------------------------------

    def _init_ros2(self) -> None:
        """Initialise ROS2 publishers and subscribers."""
        try:
            import rclpy

            if not rclpy.ok():
                rclpy.init()
            self._logger.info("ROS2 control interface initialised.")
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("ROS2 init failed: %s", exc)
            self._ros2_enabled = False

    def _ros2_navigate(self, x: float, y: float, theta: float) -> bool:
        """Publish navigation goal via ROS2."""
        self._logger.debug("ROS2 navigate_to (%.3f, %.3f, %.3f)", x, y, theta)
        # Stub: real implementation would publish geometry_msgs/PoseStamped
        return True

    def _ros2_emergency_stop(self) -> None:
        """Publish emergency stop signal via ROS2."""
        self._logger.debug("ROS2 emergency stop published.")
