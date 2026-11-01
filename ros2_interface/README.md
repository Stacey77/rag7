# ROS2 Interface — Vision Node

Self-contained ROS2 package that bridges the robotics AGI vision pipeline
with the ROS2 ecosystem.

## Prerequisites

| Requirement | Version |
|-------------|---------|
| ROS2        | Humble or later |
| Python      | 3.10+ |
| cv_bridge   | Bundled with `ros-<distro>-cv-bridge` |

All ROS2 imports are guarded with `try/except`, so the package can be
imported and unit-tested **without** a ROS2 installation.

## Build

```bash
# From the workspace root
cd ~/ros2_ws
colcon build --packages-select ros2_interface
source install/setup.bash
```

## Launch

```bash
# Default settings (CPU, all modules enabled)
ros2 launch ros2_interface vision_launch.py

# Custom device and thresholds
ros2 launch ros2_interface vision_launch.py device:=cuda confidence_threshold:=0.3

# Load parameter file directly
ros2 run ros2_interface vision_node \
    --ros-args --params-file config/vision_node_params.yaml
```

## Topics

### Subscribed

| Topic | Type | Description |
|-------|------|-------------|
| `/camera/image_raw` | `sensor_msgs/Image` | Input camera frames |

### Published

| Topic | Type | Description |
|-------|------|-------------|
| `/vision/detections` | `std_msgs/String` | JSON array of detected objects |
| `/vision/segmentation` | `sensor_msgs/Image` | Segmentation mask (`mono8`) |
| `/vision/depth` | `sensor_msgs/Image` | Depth map (`32FC1`, metres) |
| `/vision/poses` | `std_msgs/String` | JSON array of pose results |
| `/vision/scene_description` | `std_msgs/String` | Human-readable scene text |
| `/vision/pointcloud` | `sensor_msgs/PointCloud2` | 3-D point cloud |

## Services

| Service | Description | Request | Response |
|---------|-------------|---------|----------|
| `/vision/find_object` | Find a named object in the latest frame | `query: str` | JSON `{found, bbox, confidence}` |
| `/vision/analyze_scene` | Full scene analysis | *(empty trigger)* | JSON `{description, objects, spatial_map}` |

## Parameters

All parameters can be set via the launch file or a YAML parameter file.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device` | string | `"cpu"` | Compute device (`"cpu"` or `"cuda"`) |
| `enable_detection` | bool | `true` | Enable object detection |
| `enable_depth` | bool | `true` | Enable depth estimation |
| `enable_tracking` | bool | `true` | Enable multi-object tracking |
| `confidence_threshold` | float | `0.5` | Minimum detection confidence |
| `detection_model` | string | `"yolov8n"` | YOLO model variant |

## Package structure

```
ros2_interface/
├── __init__.py
├── package.xml
├── setup.cfg
├── setup_ros.py
├── config/
│   └── vision_node_params.yaml
├── launch/
│   └── vision_launch.py
└── vision_nodes/
    ├── __init__.py
    ├── image_converter.py
    ├── pointcloud_publisher.py
    ├── vision_node.py
    ├── vision_service_types.py
    └── ...
```
