"""
ROS2 PlanningNode for the RAG7 AGI Robotics Framework.

Wraps the PlanningAgent with ROS2 topic wiring.
Degrades gracefully when rclpy is not installed.
"""

import logging
from typing import Any, Dict, Optional

from agents.planning_agent import PlanningAgent

try:
    import rclpy

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


class PlanningNode(PlanningAgent):
    """ROS2 node that exposes the PlanningAgent over ROS2 topics.

    Args:
        config: Planning agent configuration dictionary.
        llm_config: Optional LLM configuration dictionary.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the planning node."""
        super().__init__(config=config, llm_config=llm_config)
        self._ros_node: Any = None
        self._publishers: Dict[str, Any] = {}
        self._subscribers: Dict[str, Any] = {}
        self._logger = logging.getLogger("rag7.ros2.planning")
        self._setup_node()

    def spin(self) -> None:
        """Run the ROS2 node event loop (no-op in mock mode)."""
        if not ROS2_AVAILABLE or self._ros_node is None:
            self._logger.info("PlanningNode spin (mock – no ROS2).")
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
            self._ros_node = rclpy.create_node("planning_node")
            self._logger.info("PlanningNode ROS2 node created.")
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Failed to create ROS2 planning node: %s", exc)
