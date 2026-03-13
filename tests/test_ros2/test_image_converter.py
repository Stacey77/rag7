"""
Tests for ImageConverter without a real ROS2 / cv_bridge installation.

cv_bridge and rclpy are mocked so the converter can be tested in any Python
environment.
"""

from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import numpy as np


# ---------------------------------------------------------------------------
# Install ROS2 mocks before importing ImageConverter
# ---------------------------------------------------------------------------


def _make_ros_image(
    height: int,
    width: int,
    encoding: str,
    data: bytes,
) -> MagicMock:
    """Return a mock ROS Image message."""
    msg = MagicMock()
    msg.height = height
    msg.width = width
    msg.encoding = encoding
    msg.data = list(data)  # ROS data is array-like
    channels_per_encoding = {"16UC1": 2, "32FC1": 4, "rgb8": 3, "bgr8": 3}
    channels = channels_per_encoding.get(encoding, 1)
    msg.step = width * channels
    msg.header = MagicMock()
    return msg


def _install_ros_mocks():
    """Inject minimal ROS2 mocks so ImageConverter can be imported."""
    if "rclpy" not in sys.modules:
        rclpy_mock = types.ModuleType("rclpy")
        sys.modules["rclpy"] = rclpy_mock

    if "sensor_msgs" not in sys.modules:
        sensor_msgs = types.ModuleType("sensor_msgs")
        sensor_msgs_msg = types.ModuleType("sensor_msgs.msg")

        class _FakeImage:
            def __init__(self):
                self.header = MagicMock()
                self.encoding = "bgr8"
                self.height = 0
                self.width = 0
                self.step = 0
                self.data = b""

        sensor_msgs_msg.Image = _FakeImage
        sensor_msgs.msg = sensor_msgs_msg
        sys.modules["sensor_msgs"] = sensor_msgs
        sys.modules["sensor_msgs.msg"] = sensor_msgs_msg

    if "builtin_interfaces" not in sys.modules:
        bi = types.ModuleType("builtin_interfaces")
        bi_msg = types.ModuleType("builtin_interfaces.msg")
        bi_msg.Time = MagicMock()
        bi.msg = bi_msg
        sys.modules["builtin_interfaces"] = bi
        sys.modules["builtin_interfaces.msg"] = bi_msg

    if "cv_bridge" not in sys.modules:
        cv_bridge = types.ModuleType("cv_bridge")
        cv_bridge.CvBridge = None  # Force fallback path in ImageConverter
        sys.modules["cv_bridge"] = cv_bridge


_install_ros_mocks()

# Force reimport without cv_bridge's CvBridge (so we exercise the manual path)
if "ros2_interface.vision_nodes.image_converter" in sys.modules:
    del sys.modules["ros2_interface.vision_nodes.image_converter"]

from ros2_interface.vision_nodes.image_converter import ImageConverter, _ROS2_AVAILABLE  # noqa: E402


class TestImageConverterRos2Available(unittest.TestCase):
    """Verify the ROS2-available flag with mocks installed."""

    def test_ros2_available(self):
        self.assertTrue(_ROS2_AVAILABLE)


class TestRosToCv2(unittest.TestCase):
    """Tests for ImageConverter.ros_to_cv2 using the manual fallback."""

    def _make_bgr_msg(self, h: int = 4, w: int = 4) -> MagicMock:
        data = np.zeros((h, w, 3), dtype=np.uint8).tobytes()
        return _make_ros_image(h, w, "bgr8", data)

    def _make_rgb_msg(self, h: int = 4, w: int = 4) -> MagicMock:
        data = np.zeros((h, w, 3), dtype=np.uint8).tobytes()
        return _make_ros_image(h, w, "rgb8", data)

    def _make_mono_msg(self, h: int = 4, w: int = 4) -> MagicMock:
        data = np.zeros((h, w), dtype=np.uint8).tobytes()
        return _make_ros_image(h, w, "mono8", data)

    def _make_16uc1_msg(self, h: int = 4, w: int = 4) -> MagicMock:
        data = np.zeros((h, w), dtype=np.uint16).tobytes()
        return _make_ros_image(h, w, "16UC1", data)

    def test_bgr8_returns_correct_shape(self):
        msg = self._make_bgr_msg()
        image = ImageConverter.ros_to_cv2(msg)
        self.assertEqual(image.shape, (4, 4, 3))

    def test_rgb8_returns_correct_shape(self):
        msg = self._make_rgb_msg()
        image = ImageConverter.ros_to_cv2(msg)
        self.assertEqual(image.shape, (4, 4, 3))

    def test_mono8_returns_2d(self):
        msg = self._make_mono_msg()
        image = ImageConverter.ros_to_cv2(msg)
        self.assertEqual(image.shape, (4, 4))

    def test_16uc1_returns_uint16(self):
        msg = self._make_16uc1_msg()
        image = ImageConverter.ros_to_cv2(msg)
        self.assertEqual(image.dtype, np.uint16)
        self.assertEqual(image.shape, (4, 4))

    def test_unsupported_encoding_raises(self):
        h, w = 4, 4
        data = np.zeros((h, w, 3), dtype=np.uint8).tobytes()
        msg = _make_ros_image(h, w, "yuv422", data)
        with self.assertRaises(ValueError):
            ImageConverter.ros_to_cv2(msg)

    def test_pixel_values_preserved(self):
        h, w = 2, 2
        arr = np.array([[[10, 20, 30], [40, 50, 60]],
                         [[70, 80, 90], [100, 110, 120]]], dtype=np.uint8)
        msg = _make_ros_image(h, w, "bgr8", arr.tobytes())
        result = ImageConverter.ros_to_cv2(msg)
        np.testing.assert_array_equal(result, arr)


class TestCv2ToRos(unittest.TestCase):
    """Tests for ImageConverter.cv2_to_ros using the manual fallback."""

    def test_bgr8_message_has_correct_shape_fields(self):
        image = np.zeros((8, 10, 3), dtype=np.uint8)
        msg = ImageConverter.cv2_to_ros(image, encoding="bgr8")
        self.assertEqual(msg.height, 8)
        self.assertEqual(msg.width, 10)
        self.assertEqual(msg.encoding, "bgr8")

    def test_mono8_message_shape(self):
        image = np.zeros((6, 8), dtype=np.uint8)
        msg = ImageConverter.cv2_to_ros(image, encoding="mono8")
        self.assertEqual(msg.height, 6)
        self.assertEqual(msg.width, 8)

    def test_frame_id_set(self):
        image = np.zeros((4, 4, 3), dtype=np.uint8)
        msg = ImageConverter.cv2_to_ros(image, encoding="bgr8", frame_id="test_frame")
        self.assertEqual(msg.header.frame_id, "test_frame")

    def test_roundtrip_bgr8(self):
        original = np.random.randint(0, 256, (4, 4, 3), dtype=np.uint8)
        msg = ImageConverter.cv2_to_ros(original, encoding="bgr8")
        # Manually reconstruct
        recovered = np.frombuffer(bytes(msg.data), dtype=np.uint8).reshape((4, 4, 3))
        np.testing.assert_array_equal(recovered, original)


class TestDepthToRos(unittest.TestCase):
    """Tests for ImageConverter.depth_to_ros."""

    def test_depth_encoding_is_32fc1(self):
        depth = np.random.rand(8, 10).astype(np.float32)
        msg = ImageConverter.depth_to_ros(depth)
        self.assertEqual(msg.encoding, "32FC1")

    def test_depth_shape_fields(self):
        depth = np.ones((12, 16), dtype=np.float32) * 3.5
        msg = ImageConverter.depth_to_ros(depth)
        self.assertEqual(msg.height, 12)
        self.assertEqual(msg.width, 16)

    def test_depth_roundtrip(self):
        depth = np.arange(100, dtype=np.float32).reshape((10, 10)) * 0.1
        msg = ImageConverter.depth_to_ros(depth)
        recovered = np.frombuffer(bytes(msg.data), dtype=np.float32).reshape((10, 10))
        np.testing.assert_array_almost_equal(recovered, depth)

    def test_depth_frame_id(self):
        depth = np.zeros((4, 4), dtype=np.float32)
        msg = ImageConverter.depth_to_ros(depth, frame_id="depth_camera")
        self.assertEqual(msg.header.frame_id, "depth_camera")


if __name__ == "__main__":
    unittest.main()
