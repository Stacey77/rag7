"""ROS2-style setup.py for the ros2_interface package.

Named setup_ros.py to avoid conflict with the root setup.py.
Install with: pip install -e . (from this directory) or via colcon build.
"""

from setuptools import find_packages, setup

package_name = "ros2_interface"

setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/vision_launch.py"]),
        ("share/" + package_name + "/config", ["config/vision_node_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="RAG7 Vision",
    maintainer_email="vision@rag7.ai",
    description="ROS2 interface for the robotics AGI vision pipeline.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "vision_node = ros2_interface.vision_nodes.vision_node:main",
        ],
    },
)
