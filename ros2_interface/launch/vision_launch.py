"""
ROS2 launch file for the vision node.

Launch with:
    ros2 launch ros2_interface vision_launch.py
    ros2 launch ros2_interface vision_launch.py device:=cuda enable_depth:=True
"""

from __future__ import annotations

try:
    from launch import LaunchDescription  # type: ignore
    from launch.actions import DeclareLaunchArgument  # type: ignore
    from launch.substitutions import LaunchConfiguration  # type: ignore
    from launch_ros.actions import Node  # type: ignore

    _LAUNCH_AVAILABLE = True
except ImportError:
    _LAUNCH_AVAILABLE = False


def generate_launch_description():
    """Generate the launch description for the vision node.

    Returns:
        LaunchDescription with the vision_node and all configurable parameters.

    Raises:
        ImportError: If ROS2 launch packages are not installed.
    """
    if not _LAUNCH_AVAILABLE:
        raise ImportError(
            "launch and launch_ros are required to use this launch file. "
            "Install them with: sudo apt install ros-<distro>-launch-ros"
        )

    # ---------------------------------------------------------------------------
    # Declare launch arguments with sensible defaults
    # ---------------------------------------------------------------------------
    device_arg = DeclareLaunchArgument(
        "device",
        default_value="cpu",
        description="Compute device for the vision pipeline (cpu or cuda).",
    )
    enable_detection_arg = DeclareLaunchArgument(
        "enable_detection",
        default_value="True",
        description="Enable object detection module.",
    )
    enable_depth_arg = DeclareLaunchArgument(
        "enable_depth",
        default_value="True",
        description="Enable monocular depth estimation module.",
    )
    enable_tracking_arg = DeclareLaunchArgument(
        "enable_tracking",
        default_value="True",
        description="Enable multi-object tracking module.",
    )
    confidence_threshold_arg = DeclareLaunchArgument(
        "confidence_threshold",
        default_value="0.5",
        description="Minimum detection confidence threshold.",
    )

    # ---------------------------------------------------------------------------
    # Vision node
    # ---------------------------------------------------------------------------
    vision_node = Node(
        package="ros2_interface",
        executable="vision_node",
        name="vision_node",
        output="screen",
        parameters=[
            {
                "device": LaunchConfiguration("device"),
                "enable_detection": LaunchConfiguration("enable_detection"),
                "enable_depth": LaunchConfiguration("enable_depth"),
                "enable_tracking": LaunchConfiguration("enable_tracking"),
                "confidence_threshold": LaunchConfiguration("confidence_threshold"),
            }
        ],
        remappings=[
            ("/camera/image_raw", "/camera/image_raw"),
        ],
    )

    return LaunchDescription(
        [
            device_arg,
            enable_detection_arg,
            enable_depth_arg,
            enable_tracking_arg,
            confidence_threshold_arg,
            vision_node,
        ]
    )
