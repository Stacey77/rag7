"""
ROS2 ControlNode for the rag7 AGI Robotics Framework.

Wraps the ControlAgent with ROS2 topic wiring.
Degrades gracefully when rclpy is not installed.
"""

import logging
from typing import Any, Dict

from agents.control_agent import ControlAgent

try:
    import rclpy

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


class ControlNode(ControlAgent):
    """ROS2 node that exposes the ControlAgent over ROS2 topics.

    Args:
        config: Control agent configuration dictionary.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the control node."""
        super().__init__(config=config, ros2_enabled=ROS2_AVAILABLE)
        self._ros_node: Any = None
        self._publishers: Dict[str, Any] = {}
        self._subscribers: Dict[str, Any] = {}
        self._logger = logging.getLogger("rag7.ros2.control")
        self._setup_node()

    def spin(self) -> None:
        """Run the ROS2 node event loop (no-op in mock mode)."""
        if not ROS2_AVAILABLE or self._ros_node is None:
            self._logger.info("ControlNode spin (mock – no ROS2).")
            return
        try:
            rclpy.spin(self._ros_node)
        except KeyboardInterrupt:
            pass
        finally:
            self._ros_node.destroy_node()

    def _setup_node(self) -> None:
        """Create the ROS2 node and wire up topics."""
        if not ROS2_AVAILABLE:
            self._logger.info("rclpy not available; running in mock mode.")
            return
        try:
            if not rclpy.ok():
                rclpy.init()
            self._ros_node = rclpy.create_node("control_node")
            self._logger.info("ControlNode ROS2 node created.")
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Failed to create ROS2 control node: %s", exc)
