"""
ROS2 launch file for the Resolver Agent node.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    resolver_node = Node(
        package="rag7",
        executable="resolver_node",
        name="resolver_agent_node",
        output="screen",
        parameters=[
            {"monitoring_rate": 10.0},
            {"health_check_rate": 1.0},
        ],
        remappings=[
            ("/agents/perception/status", "/agents/perception/status"),
            ("/agents/planning/status", "/agents/planning/status"),
            ("/agents/control/status", "/agents/control/status"),
            ("/agents/communication/status", "/agents/communication/status"),
            ("/agents/coordination/status", "/agents/coordination/status"),
        ],
    )

    return LaunchDescription([resolver_node])
