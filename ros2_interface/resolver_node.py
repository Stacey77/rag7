"""
ROS2 Resolver Node for the Resolver Agent.

This node provides the ROS2 interface for the Resolver Agent, subscribing to
agent status topics, handling error reports, and publishing resolutions and
health data.

Note: This module requires ROS2 (rclpy) to run. When rclpy is not available,
the module defines stub classes to allow import and testing without ROS2.
"""

import logging
import time
from typing import Any, Dict

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String

    _ROS2_AVAILABLE = True
except ImportError:
    _ROS2_AVAILABLE = False

    # ---------------------------------------------------------------------------
    # Minimal stubs so the module can be imported without a ROS2 installation
    # ---------------------------------------------------------------------------

    class Node:  # type: ignore[no-redef]
        """Stub ROS2 Node for non-ROS environments."""

        def __init__(self, node_name: str, **kwargs):
            self._node_name = node_name
            self._logger = logging.getLogger(f"ros2.{node_name}")

        def get_logger(self):
            return self._logger

        def create_subscription(self, *args, **kwargs):
            return None

        def create_publisher(self, *args, **kwargs):
            return _StubPublisher()

        def create_service(self, *args, **kwargs):
            return None

        def create_timer(self, *args, **kwargs):
            return None

    class _StubPublisher:
        def publish(self, msg):
            pass

    class String:  # type: ignore[no-redef]
        def __init__(self):
            self.data = ""


logger = logging.getLogger(__name__)

from agents.resolver_agent import ResolverAgent  # noqa: E402


class ResolverNode(Node):
    """
    ROS2 node for the Resolver Agent.

    Topics subscribed:
        /agents/perception/status
        /agents/planning/status
        /agents/control/status
        /agents/communication/status
        /agents/coordination/status
        /system/errors
        /system/conflicts

    Topics published:
        /resolver/resolutions
        /resolver/health_status
        /resolver/alerts
        /resolver/recovery_actions

    Services (when ROS2 is available):
        /resolver/resolve_conflict
        /resolver/recover_error
        /resolver/get_health_status
        /resolver/arbitrate_request

    Timer:
        health_check_timer  – 1 Hz
    """

    HEALTH_CHECK_RATE = 1.0  # Hz

    def __init__(self):
        super().__init__("resolver_agent_node")
        self.resolver = ResolverAgent()

        self._setup_subscriptions()
        self._setup_publishers()
        self._setup_timer()

        self.resolver.start()
        self.get_logger().info("ResolverNode initialized")  # type: ignore[attr-defined]

    # ------------------------------------------------------------------ #
    # Setup
    # ------------------------------------------------------------------ #

    def _setup_subscriptions(self) -> None:
        """Subscribe to all agent status and system error topics."""
        agent_topics = [
            "/agents/perception/status",
            "/agents/planning/status",
            "/agents/control/status",
            "/agents/communication/status",
            "/agents/coordination/status",
        ]
        for topic in agent_topics:
            self.create_subscription(  # type: ignore[attr-defined]
                String, topic, self.handle_agent_status, 10
            )

        self.create_subscription(  # type: ignore[attr-defined]
            String, "/system/errors", self.handle_error_report, 10
        )
        self.create_subscription(  # type: ignore[attr-defined]
            String, "/system/conflicts", self.handle_conflict_report, 10
        )

    def _setup_publishers(self) -> None:
        """Create publishers for resolver outputs."""
        self._pub_resolutions = self.create_publisher(  # type: ignore[attr-defined]
            String, "/resolver/resolutions", 10
        )
        self._pub_health = self.create_publisher(  # type: ignore[attr-defined]
            String, "/resolver/health_status", 10
        )
        self._pub_alerts = self.create_publisher(  # type: ignore[attr-defined]
            String, "/resolver/alerts", 10
        )
        self._pub_recovery = self.create_publisher(  # type: ignore[attr-defined]
            String, "/resolver/recovery_actions", 10
        )

    def _setup_timer(self) -> None:
        """Create the periodic health check timer (1 Hz)."""
        self.create_timer(  # type: ignore[attr-defined]
            1.0 / self.HEALTH_CHECK_RATE, self.health_check_timer
        )

    # ------------------------------------------------------------------ #
    # Callbacks
    # ------------------------------------------------------------------ #

    def handle_agent_status(self, msg: Any) -> None:
        """Process agent status updates from subscribed topics."""
        import json  # pylint: disable=import-outside-toplevel

        try:
            data: Dict[str, Any] = json.loads(msg.data)
            agent_name = data.get("agent", "unknown")
            logger.debug("Received status from agent '%s'", agent_name)
            # Forward to health monitor via resolver
            self.resolver.health_monitor.update_agent_health(
                agent_name, _DictState(data)
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to process agent status: %s", exc)

    def handle_error_report(self, msg: Any) -> None:
        """Handle error reports from /system/errors."""
        import json  # pylint: disable=import-outside-toplevel

        try:
            error: Dict[str, Any] = json.loads(msg.data)
            result = self.resolver.recover_from_error(error)
            self.publish_recovery_action(result)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to handle error report: %s", exc)

    def handle_conflict_report(self, msg: Any) -> None:
        """Handle conflict reports from /system/conflicts."""
        import json  # pylint: disable=import-outside-toplevel

        try:
            conflict: Dict[str, Any] = json.loads(msg.data)
            resolution = self.resolver.resolve_conflict(conflict)
            self.publish_resolution(resolution)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to handle conflict report: %s", exc)

    def health_check_timer(self) -> None:
        """Periodic health check callback (1 Hz)."""
        import json  # pylint: disable=import-outside-toplevel

        health = self.resolver.assess_system_health()
        msg = String()
        msg.data = json.dumps(health)
        self._pub_health.publish(msg)

        for alert in health.get("alerts", []):
            alert_msg = String()
            alert_msg.data = json.dumps(alert)
            self._pub_alerts.publish(alert_msg)

    # ------------------------------------------------------------------ #
    # Publishers
    # ------------------------------------------------------------------ #

    def publish_resolution(self, resolution: Dict[str, Any]) -> None:
        """Publish a conflict resolution to /resolver/resolutions."""
        import json  # pylint: disable=import-outside-toplevel

        msg = String()
        msg.data = json.dumps(resolution)
        self._pub_resolutions.publish(msg)

    def publish_recovery_action(self, action: Dict[str, Any]) -> None:
        """Publish a recovery action to /resolver/recovery_actions."""
        import json  # pylint: disable=import-outside-toplevel

        msg = String()
        msg.data = json.dumps(action)
        self._pub_recovery.publish(msg)


# ---------------------------------------------------------------------------
# Helper: thin wrapper to expose a dict as an object with attribute access
# ---------------------------------------------------------------------------

class _DictState:
    """Adapts a plain dict to the attribute-access API expected by HealthMonitor."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._data.get(name, None)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Launch the ROS2 ResolverNode."""
    if not _ROS2_AVAILABLE:
        logger.error("rclpy is not installed; cannot launch ROS2 node")
        return

    rclpy.init()
    node = ResolverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.resolver.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
