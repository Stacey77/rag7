"""
ROS2 interface module for the RAG7 AGI Robotics Framework.

Provides a thin wrapper around rclpy for publish/subscribe and
service-call operations.
"""

import logging
from typing import Any, Callable, Dict, Optional

try:
    import rclpy
    from rclpy.node import Node

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


class ROS2Interface:
    """Thin abstraction layer over ROS2 communication primitives.

    Wraps rclpy publish, subscribe, and service-call operations.
    Falls back to a mock implementation when rclpy is not installed.

    Args:
        node_name: Name for the underlying ROS2 node.
    """

    def __init__(self, node_name: str = "rag7_interface") -> None:
        """Initialize the ROS2 interface."""
        self._logger = logging.getLogger("rag7.ros2_interface")
        self._node_name = node_name
        self._node: Optional[Any] = None
        self._publishers: Dict[str, Any] = {}
        self._subscribers: Dict[str, Any] = {}

        if ROS2_AVAILABLE:
            self._init_ros2()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def publish(self, topic: str, message: Any) -> bool:
        """Publish a message to a ROS2 topic.

        Args:
            topic: Topic name string.
            message: Message object to publish.

        Returns:
            True if the message was published successfully.
        """
        if not ROS2_AVAILABLE or self._node is None:
            self._logger.debug("Mock publish to '%s': %s", topic, message)
            return True
        try:
            if topic in self._publishers:
                self._publishers[topic].publish(message)
            return True
        except Exception as exc:  # noqa: BLE001
            self._logger.error("Publish failed on '%s': %s", topic, exc)
            return False

    def subscribe(self, topic: str, callback: Callable[[Any], None]) -> bool:
        """Subscribe to a ROS2 topic.

        Args:
            topic: Topic name string.
            callback: Function to call when a message is received.

        Returns:
            True if the subscription was set up successfully.
        """
        if not ROS2_AVAILABLE or self._node is None:
            self._logger.debug("Mock subscribe to '%s'.", topic)
            self._subscribers[topic] = callback
            return True
        try:
            # Real subscription would require a message type; stored as stub
            self._subscribers[topic] = callback
            return True
        except Exception as exc:  # noqa: BLE001
            self._logger.error("Subscribe failed on '%s': %s", topic, exc)
            return False

    def call_service(self, service: str, request: Any) -> Optional[Any]:
        """Call a ROS2 service.

        Args:
            service: Service name string.
            request: Service request object.

        Returns:
            Service response, or None on failure.
        """
        if not ROS2_AVAILABLE or self._node is None:
            self._logger.debug("Mock service call to '%s'.", service)
            return {"status": "mock_response"}
        try:
            # Stub; real implementation would use rclpy service clients
            return None
        except Exception as exc:  # noqa: BLE001
            self._logger.error("Service call failed on '%s': %s", service, exc)
            return None

    def is_available(self) -> bool:
        """Check whether the ROS2 interface is available.

        Returns:
            True if rclpy is installed and the node is running.
        """
        return ROS2_AVAILABLE and self._node is not None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _init_ros2(self) -> None:
        """Attempt to initialise the underlying rclpy node."""
        try:
            if not rclpy.ok():
                rclpy.init()
            self._node = rclpy.create_node(self._node_name)
            self._logger.info("ROS2 node '%s' created.", self._node_name)
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("ROS2 initialisation failed: %s", exc)
