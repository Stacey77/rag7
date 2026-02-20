"""
Sensor fusion module for the rag7 perception system.

Fuses data from RGB-D camera, 2-D LiDAR, and IMU into a unified
robot state estimate.
"""

import logging
from typing import Any, Dict, Optional

import numpy as np


class SensorFusion:
    """Multi-modal sensor fusion processor.

    Combines camera depth, LiDAR range, and IMU orientation data into
    a coherent fused state using a lightweight complementary-filter
    approach.

    Attributes:
        _state: Current fused state dictionary.
    """

    def __init__(self) -> None:
        """Initialize the sensor fusion module."""
        self._logger = logging.getLogger("rag7.perception.fusion")
        self._state: Dict[str, Any] = {
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            "velocity": {"linear": 0.0, "angular": 0.0},
            "obstacles": [],
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fuse(
        self,
        camera_data: Optional[Dict[str, Any]],
        lidar_data: Optional[Any],
        imu_data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Fuse data from multiple sensors into a unified state estimate.

        Args:
            camera_data: Dict with optional ``depth`` array and
                ``detections`` list.
            lidar_data: Array-like of LiDAR range measurements.
            imu_data: Dict with ``acceleration`` and/or orientation keys.

        Returns:
            Fused state dictionary with ``position``, ``orientation``,
            ``obstacles``, and ``confidence`` keys.
        """
        fused: Dict[str, Any] = {
            "position": dict(self._state["position"]),
            "orientation": dict(self._state["orientation"]),
            "obstacles": [],
            "confidence": 0.0,
        }

        confidence_sources = 0

        if camera_data is not None:
            depth = camera_data.get("depth")
            if depth is not None:
                pos_3d = self._camera_to_3d(camera_data, depth)
                fused["position"].update(pos_3d)
                confidence_sources += 1

        if lidar_data is not None:
            try:
                ranges = np.asarray(lidar_data, dtype=float)
                valid = ranges[np.isfinite(ranges) & (ranges > 0)]
                if len(valid) > 0:
                    fused["obstacles"] = [float(np.min(valid))]
                    confidence_sources += 1
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("LiDAR fusion error: %s", exc)

        if imu_data is not None:
            updated = self._apply_imu(fused, imu_data)
            fused["orientation"] = updated["orientation"]
            confidence_sources += 1

        fused["confidence"] = confidence_sources / 3.0
        self._state = fused
        return fused

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _camera_to_3d(
        self, camera_data: Dict[str, Any], depth: Any
    ) -> Dict[str, float]:
        """Project camera depth data to a 3-D position estimate.

        Uses the image centre pixel depth as a simplified projection.

        Args:
            camera_data: Camera data dictionary (unused fields reserved
                for future intrinsic calibration).
            depth: Depth array (H x W) in metres.

        Returns:
            Position dictionary with ``x``, ``y``, ``z`` keys.
        """
        try:
            depth_arr = np.asarray(depth, dtype=float)
            if depth_arr.ndim == 2:
                h, w = depth_arr.shape
                centre_depth = float(depth_arr[h // 2, w // 2])
                return {"x": 0.0, "y": 0.0, "z": centre_depth}
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Camera projection error: %s", exc)
        return {"x": 0.0, "y": 0.0, "z": 0.0}

    def _apply_imu(
        self, state: Dict[str, Any], imu_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply IMU measurements to correct the orientation estimate.

        Args:
            state: Current fused state dict.
            imu_data: IMU reading dict with optional ``roll``, ``pitch``,
                ``yaw``, or ``angular_velocity`` keys.

        Returns:
            Updated state dictionary.
        """
        orientation = dict(state.get("orientation", {}))
        orientation["roll"] = float(imu_data.get("roll", orientation.get("roll", 0.0)))
        orientation["pitch"] = float(imu_data.get("pitch", orientation.get("pitch", 0.0)))
        orientation["yaw"] = float(imu_data.get("yaw", orientation.get("yaw", 0.0)))
        return {**state, "orientation": orientation}
