"""
PointCloudPublisher — utility for converting numpy point arrays to
sensor_msgs/PointCloud2 messages.

All ROS2 imports are guarded with try/except so this module can be imported
without a ROS2 installation.
"""

from __future__ import annotations

import logging
import struct
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional ROS2 imports
# ---------------------------------------------------------------------------

_ROS2_AVAILABLE = False
try:
    import rclpy  # type: ignore  # noqa: F401
    from sensor_msgs.msg import PointCloud2, PointField  # type: ignore
    from std_msgs.msg import Header  # type: ignore

    _ROS2_AVAILABLE = True
except ImportError:
    PointCloud2 = None  # type: ignore[assignment,misc]
    PointField = None  # type: ignore[assignment,misc]
    Header = None  # type: ignore[assignment,misc]


class PointCloudPublisher:
    """Helper class for converting numpy point arrays to PointCloud2 messages.

    Example::

        publisher = PointCloudPublisher()
        msg = publisher.array_to_pointcloud2(points, frame_id='map')
    """

    # XYZ field definitions (reused for every cloud)
    _FIELDS_XYZ = None  # populated lazily when ROS2 is available

    @classmethod
    def _get_xyz_fields(cls) -> list:
        """Return the three PointField definitions for XYZ clouds."""
        if cls._FIELDS_XYZ is None:
            if not _ROS2_AVAILABLE:
                raise ImportError(
                    "rclpy is not installed.  Install ROS2 and source the "
                    "environment to use PointCloudPublisher."
                )
            cls._FIELDS_XYZ = [
                PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            ]
        return cls._FIELDS_XYZ

    @staticmethod
    def array_to_pointcloud2(
        points: np.ndarray,
        stamp: Optional[Any] = None,
        frame_id: str = "map",
    ) -> Any:
        """Convert an Nx3 float32 numpy array to a sensor_msgs/PointCloud2.

        Args:
            points: numpy array of shape ``(N, 3)`` with XYZ coordinates.
            stamp: Optional ``builtin_interfaces/Time`` stamp.
            frame_id: TF frame identifier for the cloud.

        Returns:
            ``sensor_msgs/PointCloud2`` message.

        Raises:
            ImportError: If rclpy is not installed.
            ValueError: If *points* does not have shape ``(N, 3)``.
        """
        if not _ROS2_AVAILABLE:
            raise ImportError(
                "rclpy is not installed.  Install ROS2 and source the "
                "environment to use PointCloudPublisher."
            )

        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError(
                f"points must have shape (N, 3), got {points.shape}"
            )

        cloud = PointCloud2()
        cloud.header.frame_id = frame_id
        if stamp is not None:
            cloud.header.stamp = stamp

        num_points = points.shape[0]
        point_step = 12  # 3 × float32 = 12 bytes
        row_step = point_step * num_points

        cloud.height = 1
        cloud.width = num_points
        cloud.fields = PointCloudPublisher._get_xyz_fields()
        cloud.is_bigendian = False
        cloud.point_step = point_step
        cloud.row_step = row_step
        cloud.is_dense = bool(np.isfinite(points).all())

        # Pack as little-endian float32 triples
        pts_float32 = points.astype(np.float32)
        cloud.data = pts_float32.tobytes()

        return cloud

    @staticmethod
    def pointcloud2_to_array(msg: Any) -> np.ndarray:
        """Convert a sensor_msgs/PointCloud2 back to an Nx3 numpy array.

        Args:
            msg: ``sensor_msgs/PointCloud2`` message.

        Returns:
            numpy array of shape ``(N, 3)`` with float32 XYZ values.

        Raises:
            ImportError: If rclpy is not installed.
        """
        if not _ROS2_AVAILABLE:
            raise ImportError(
                "rclpy is not installed.  Install ROS2 and source the "
                "environment to use PointCloudPublisher."
            )

        raw = np.frombuffer(bytes(msg.data), dtype=np.float32)
        num_fields = msg.point_step // 4  # bytes per point / bytes per float32
        points = raw.reshape((-1, num_fields))[:, :3]
        return points
