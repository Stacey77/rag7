"""
ROS2 launch file for the rag7 AGI system.

Launches the perception, planning, and control nodes together.
"""

try:
    from launch import LaunchDescription
    from launch_ros.actions import Node

    def generate_launch_description() -> LaunchDescription:
        """Generate the ROS2 launch description for the rag7 AGI system.

        Returns:
            LaunchDescription with all three AGI nodes.
        """
        perception_node = Node(
            package="rag7_agi",
            executable="perception_node",
            name="perception_node",
            output="screen",
        )

        planning_node = Node(
            package="rag7_agi",
            executable="planning_node",
            name="planning_node",
            output="screen",
        )

        control_node = Node(
            package="rag7_agi",
            executable="control_node",
            name="control_node",
            output="screen",
        )

        return LaunchDescription([perception_node, planning_node, control_node])

except ImportError:
    # Provide a stub when launch packages are not installed
    def generate_launch_description():  # type: ignore[misc]
        """Stub launch description (ROS2 launch not available)."""
        return None
