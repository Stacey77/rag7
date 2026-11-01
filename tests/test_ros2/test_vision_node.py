"""
Tests for VisionNode without a real ROS2 installation.

rclpy is mocked so the node can be imported and exercised in any Python
environment.
"""

from __future__ import annotations

import json
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Mock the entire rclpy stack before importing vision_node
# ---------------------------------------------------------------------------


def _build_rclpy_mock() -> types.ModuleType:
    """Return a mock rclpy module with the minimal API used by vision_node."""
    rclpy_mock = types.ModuleType("rclpy")
    rclpy_mock.init = MagicMock()
    rclpy_mock.spin = MagicMock()
    rclpy_mock.shutdown = MagicMock()

    # rclpy.node
    node_mod = types.ModuleType("rclpy.node")

    class _Node:
        def __init__(self, name, **kwargs):
            self._name = name

        def get_logger(self):
            import logging
            return logging.getLogger(self._name)

        def create_subscription(self, *a, **kw):
            return MagicMock()

        def create_publisher(self, *a, **kw):
            return MagicMock()

        def create_service(self, *a, **kw):
            return MagicMock()

        def destroy_node(self):
            pass

    node_mod.Node = _Node
    rclpy_mock.node = node_mod

    # rclpy.qos
    qos_mod = types.ModuleType("rclpy.qos")
    qos_mod.QoSProfile = MagicMock(return_value=MagicMock())
    qos_mod.ReliabilityPolicy = MagicMock()
    qos_mod.HistoryPolicy = MagicMock()
    rclpy_mock.qos = qos_mod

    return rclpy_mock


def _build_sensor_msgs_mock() -> types.ModuleType:
    sensor_msgs = types.ModuleType("sensor_msgs")
    sensor_msgs_msg = types.ModuleType("sensor_msgs.msg")

    class _Image:
        def __init__(self):
            self.header = MagicMock()
            self.encoding = "bgr8"
            self.height = 10
            self.width = 10
            self.step = 30
            self.data = b"\x00" * 300

    sensor_msgs_msg.Image = _Image
    sensor_msgs_msg.PointCloud2 = MagicMock()
    sensor_msgs.msg = sensor_msgs_msg
    return sensor_msgs, sensor_msgs_msg


def _install_ros2_mocks():
    """Install minimal ROS2 mocks into sys.modules."""
    rclpy_mock = _build_rclpy_mock()
    sys.modules["rclpy"] = rclpy_mock
    sys.modules["rclpy.node"] = rclpy_mock.node
    sys.modules["rclpy.qos"] = rclpy_mock.qos

    sensor_msgs, sensor_msgs_msg = _build_sensor_msgs_mock()
    sys.modules["sensor_msgs"] = sensor_msgs
    sys.modules["sensor_msgs.msg"] = sensor_msgs_msg

    std_msgs = types.ModuleType("std_msgs")
    std_msgs_msg = types.ModuleType("std_msgs.msg")

    class _String:
        data: str = ""

    std_msgs_msg.String = _String
    std_msgs.msg = std_msgs_msg
    sys.modules["std_msgs"] = std_msgs
    sys.modules["std_msgs.msg"] = std_msgs_msg

    geometry_msgs = types.ModuleType("geometry_msgs")
    sys.modules["geometry_msgs"] = geometry_msgs

    vision_msgs = types.ModuleType("vision_msgs")
    sys.modules["vision_msgs"] = vision_msgs

    cv_bridge = types.ModuleType("cv_bridge")
    cv_bridge.CvBridge = MagicMock()
    sys.modules["cv_bridge"] = cv_bridge

    builtin_interfaces = types.ModuleType("builtin_interfaces")
    builtin_interfaces_msg = types.ModuleType("builtin_interfaces.msg")
    builtin_interfaces_msg.Time = MagicMock()
    builtin_interfaces.msg = builtin_interfaces_msg
    sys.modules["builtin_interfaces"] = builtin_interfaces
    sys.modules["builtin_interfaces.msg"] = builtin_interfaces_msg


# Install mocks at module-import time so that vision_node picks them up.
_install_ros2_mocks()

# Now we can safely import the vision node
from ros2_interface.vision_nodes.vision_node import VisionNode, _ROS2_AVAILABLE  # noqa: E402


class TestVisionNodeInit(unittest.TestCase):
    """Test VisionNode constructor without real ROS2."""

    def test_node_instantiates(self):
        node = VisionNode(device="cpu", enable_detection=False)
        self.assertIsNotNone(node)

    def test_default_device(self):
        node = VisionNode()
        self.assertEqual(node.device, "cpu")

    def test_custom_params(self):
        node = VisionNode(
            device="cpu",
            enable_detection=True,
            enable_depth=False,
            enable_tracking=False,
            confidence_threshold=0.3,
        )
        self.assertTrue(node.enable_detection)
        self.assertFalse(node.enable_depth)
        self.assertAlmostEqual(node.confidence_threshold, 0.3)

    def test_pipeline_initially_none(self):
        node = VisionNode()
        self.assertIsNone(node._pipeline)


class TestVisionNodePipelineLazyLoad(unittest.TestCase):
    """Test that the pipeline is lazily initialised."""

    def test_pipeline_created_on_access(self):
        node = VisionNode(device="cpu", enable_detection=False)
        with patch("vision.vision_pipeline.VisionPipeline.__init__", return_value=None):
            pipeline = node.pipeline
        self.assertIsNotNone(pipeline)

    def test_pipeline_reused_on_second_access(self):
        node = VisionNode(device="cpu", enable_detection=False)
        mock_pipeline = MagicMock()
        node._pipeline = mock_pipeline
        self.assertIs(node.pipeline, mock_pipeline)


class TestVisionNodeCallbacks(unittest.TestCase):
    """Test service and image callbacks with mocked internals."""

    def setUp(self):
        self.node = VisionNode(device="cpu", enable_detection=False)
        # Inject a mock pipeline
        self.mock_pipeline = MagicMock()
        self.mock_pipeline.process_frame.return_value = MagicMock(
            detections=[],
            segmentation=None,
            depth_map=None,
            poses=[],
            tracks=[],
            scene_description="",
        )
        self.mock_pipeline.find_object.return_value = {"score": 0.85, "region": [10, 20, 50, 60]}
        self.mock_pipeline.analyze_scene.return_value = {
            "description": "A test scene.",
            "detections": [],
            "depth_available": False,
        }
        self.node._pipeline = self.mock_pipeline

    def test_find_object_callback_no_image(self):
        """find_object_callback returns a valid JSON response when no last image."""
        request = MagicMock()
        request.query = "red cup"
        response = MagicMock()
        response.data = ""

        result = self.node.find_object_callback(request, response)
        data = json.loads(result.data)
        self.assertIn("found", data)
        self.assertIn("bbox", data)
        self.assertIn("confidence", data)

    def test_analyze_scene_callback_no_image(self):
        """analyze_scene_callback returns a valid JSON response when no last image."""
        request = MagicMock()
        response = MagicMock()
        response.data = ""

        result = self.node.analyze_scene_callback(request, response)
        data = json.loads(result.data)
        self.assertIn("description", data)
        self.assertIn("objects", data)
        self.assertIn("spatial_map", data)

    def test_find_object_callback_with_last_image(self):
        """find_object_callback uses the stored image when available."""
        import numpy as np

        self.node._last_image = np.zeros((100, 100, 3), dtype=np.uint8)

        request = MagicMock()
        request.query = "chair"
        response = MagicMock()
        response.data = ""

        result = self.node.find_object_callback(request, response)
        data = json.loads(result.data)
        self.assertIn("found", data)


class TestVisionNodeImageCallback(unittest.TestCase):
    """Test image_callback with a mocked pipeline and converter."""

    def test_image_callback_bad_conversion_does_not_raise(self):
        """image_callback should log and return on conversion error."""
        node = VisionNode(device="cpu", enable_detection=False)
        msg = MagicMock()
        # Patch converter to raise, should not propagate
        with patch(
            "ros2_interface.vision_nodes.image_converter.ImageConverter.ros_to_cv2",
            side_effect=Exception("conversion error"),
        ):
            # Should not raise
            node.image_callback(msg)


class TestVisionNodeROS2Flag(unittest.TestCase):
    """Test that the _ROS2_AVAILABLE flag reflects mocked state."""

    def test_ros2_available_with_mocks(self):
        # Since we injected mocks, _ROS2_AVAILABLE should be True
        self.assertTrue(_ROS2_AVAILABLE)


if __name__ == "__main__":
    unittest.main()
