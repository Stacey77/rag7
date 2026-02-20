"""
ROS2 PerceptionNode for the RAG7 AGI Robotics Framework.

Wraps the PerceptionAgent with ROS2 subscriber/publisher wiring.
Degrades gracefully when rclpy is not installed.
"""

import logging
from typing import Any, Dict

from agents.perception_agent import PerceptionAgent

try:
    import rclpy
    from rclpy.node import Node

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


class PerceptionNode(PerceptionAgent):
    """ROS2 node that exposes the PerceptionAgent over ROS2 topics.

    Subscribes to camera, LiDAR, and IMU topics and publishes
    processed perception outputs.

    Args:
        config: Perception agent configuration dictionary.
        device: Compute device for inference.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        device: str = "cpu",
    ) -> None:
        """Initialize the perception node."""
        super().__init__(config=config, device=device)
        self._ros_node: Any = None
        self._publishers: Dict[str, Any] = {}
        self._subscribers: Dict[str, Any] = {}
        self._logger = logging.getLogger("rag7.ros2.perception")

        self._setup_node()

    # ------------------------------------------------------------------
    # Node lifecycle
    # ------------------------------------------------------------------

    def spin(self) -> None:
        """Run the ROS2 node event loop.

        Blocks until the node is shut down.  In non-ROS mode, this is
        a no-op.
        """
        if not ROS2_AVAILABLE or self._ros_node is None:
            self._logger.info("PerceptionNode spin (mock – no ROS2).")
            return
        try:
            rclpy.spin(self._ros_node)
        except KeyboardInterrupt:
            pass
        finally:
            self._ros_node.destroy_node()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _setup_node(self) -> None:
        """Create the ROS2 node and wire up topics."""
        if not ROS2_AVAILABLE:
            self._logger.info("rclpy not available; running in mock mode.")
            return
        try:
            if not rclpy.ok():
                rclpy.init()
            self._ros_node = rclpy.create_node("perception_node")
            # Real wiring would add typed subscribers/publishers here
            self._logger.info("PerceptionNode ROS2 node created.")
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Failed to create ROS2 perception node: %s", exc)
