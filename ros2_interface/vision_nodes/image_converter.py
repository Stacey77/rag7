"""
ImageConverter — utilities for converting between ROS Image messages and
numpy arrays.

All cv_bridge and rclpy imports are guarded so this module can be imported
and used in unit tests without a ROS2 installation.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional ROS2 / cv_bridge imports
# ---------------------------------------------------------------------------

_ROS2_AVAILABLE = False
_CV_BRIDGE_AVAILABLE = False

try:
    import rclpy  # type: ignore  # noqa: F401
    from sensor_msgs.msg import Image as RosImage  # type: ignore
    from builtin_interfaces.msg import Time  # type: ignore

    _ROS2_AVAILABLE = True
except ImportError:
    RosImage = None  # type: ignore[assignment,misc]
    Time = None  # type: ignore[assignment,misc]

try:
    from cv_bridge import CvBridge  # type: ignore

    if CvBridge is not None and callable(CvBridge):
        _CV_BRIDGE = CvBridge()
        _CV_BRIDGE_AVAILABLE = True
    else:
        _CV_BRIDGE = None  # type: ignore[assignment]
except ImportError:
    _CV_BRIDGE = None  # type: ignore[assignment]

# Encoding → numpy dtype mapping (used when cv_bridge is unavailable)
_ENCODING_DTYPE: dict = {
    "rgb8": (np.uint8, 3),
    "bgr8": (np.uint8, 3),
    "mono8": (np.uint8, 1),
    "16UC1": (np.uint16, 1),
    "32FC1": (np.float32, 1),
}


class ImageConverter:
    """Convert between ROS ``sensor_msgs/Image`` messages and numpy arrays.

    The class falls back to a manual byte-level conversion when cv_bridge is
    not installed, covering the most common encodings.
    """

    @staticmethod
    def ros_to_cv2(msg: Any, desired_encoding: str = "passthrough") -> np.ndarray:
        """Convert a ROS Image message to a numpy array.

        Supports ``rgb8``, ``bgr8``, ``mono8``, and ``16UC1`` encodings.
        When cv_bridge is available it is used directly; otherwise a manual
        conversion is performed.

        Args:
            msg: ``sensor_msgs/Image`` ROS message.
            desired_encoding: Target encoding.  ``"passthrough"`` keeps the
                              original encoding.

        Returns:
            numpy array of shape ``(H, W)`` or ``(H, W, C)``.

        Raises:
            ImportError: If rclpy is not installed.
        """
        if not _ROS2_AVAILABLE:
            raise ImportError(
                "rclpy is not installed.  Install ROS2 and source the "
                "environment to use ImageConverter."
            )

        if _CV_BRIDGE_AVAILABLE and _CV_BRIDGE is not None:
            return _CV_BRIDGE.imgmsg_to_cv2(msg, desired_encoding)

        # Manual fallback
        encoding = msg.encoding.lower().replace("-", "").replace("_", "")
        height, width = msg.height, msg.width

        dtype_map = {
            "rgb8": (np.uint8, 3),
            "bgr8": (np.uint8, 3),
            "mono8": (np.uint8, 1),
            "16uc1": (np.uint16, 1),
            "32fc1": (np.float32, 1),
        }
        if encoding not in dtype_map:
            raise ValueError(f"Unsupported encoding for manual conversion: {encoding}")

        dtype, channels = dtype_map[encoding]
        array = np.frombuffer(bytes(msg.data), dtype=dtype)
        if channels == 1:
            image = array.reshape((height, width))
        else:
            image = array.reshape((height, width, channels))
        return image

    @staticmethod
    def cv2_to_ros(
        image: np.ndarray,
        encoding: str = "bgr8",
        stamp: Optional[Any] = None,
        frame_id: str = "camera",
    ) -> Any:
        """Convert a numpy array to a ROS Image message.

        Args:
            image: numpy array ``(H, W, C)`` or ``(H, W)``.
            encoding: ROS image encoding string, e.g. ``"bgr8"`` or
                      ``"mono8"``.
            stamp: Optional ``builtin_interfaces/Time`` stamp.
            frame_id: TF frame identifier.

        Returns:
            ``sensor_msgs/Image`` ROS message.

        Raises:
            ImportError: If rclpy is not installed.
        """
        if not _ROS2_AVAILABLE:
            raise ImportError(
                "rclpy is not installed.  Install ROS2 and source the "
                "environment to use ImageConverter."
            )

        if _CV_BRIDGE_AVAILABLE and _CV_BRIDGE is not None:
            msg = _CV_BRIDGE.cv2_to_imgmsg(image, encoding=encoding)
        else:
            # Manual fallback
            msg = RosImage()
            msg.encoding = encoding
            msg.height = image.shape[0]
            msg.width = image.shape[1]
            msg.step = image.shape[1] * image.itemsize * (
                image.shape[2] if image.ndim == 3 else 1
            )
            msg.data = image.tobytes()

        if stamp is not None:
            msg.header.stamp = stamp
        msg.header.frame_id = frame_id
        return msg

    @staticmethod
    def depth_to_ros(
        depth_map: np.ndarray,
        stamp: Optional[Any] = None,
        frame_id: str = "camera",
    ) -> Any:
        """Convert a float32 depth map to a ROS Image message (32FC1 encoding).

        Args:
            depth_map: numpy array ``(H, W)`` of float32 depth values in
                       metres.
            stamp: Optional ``builtin_interfaces/Time`` stamp.
            frame_id: TF frame identifier.

        Returns:
            ``sensor_msgs/Image`` ROS message with encoding ``"32FC1"``.

        Raises:
            ImportError: If rclpy is not installed.
        """
        if not _ROS2_AVAILABLE:
            raise ImportError(
                "rclpy is not installed.  Install ROS2 and source the "
                "environment to use ImageConverter."
            )

        depth = depth_map.astype(np.float32)
        return ImageConverter.cv2_to_ros(
            depth, encoding="32FC1", stamp=stamp, frame_id=frame_id
        )
