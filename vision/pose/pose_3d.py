"""Lift 2-D poses to 3-D using depth information."""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

from vision.pose.human_pose_estimator import PoseResult

logger = logging.getLogger(__name__)


class Pose3DEstimator:
    """Lift 2-D skeleton keypoints to 3-D using a depth map.

    Each 2-D keypoint ``(u, v)`` is back-projected to 3-D using:

    .. code-block::

        x = (u - cx) * Z / fx
        y = (v - cy) * Z / fy
        z = Z   (sampled from depth map)

    Example::

        estimator = Pose3DEstimator(fx=525, fy=525, cx=319.5, cy=239.5)
        poses_3d = estimator.lift(pose_2d_list, depth_map)
    """

    def __init__(
        self,
        fx: float = 525.0,
        fy: float = 525.0,
        cx: float = 319.5,
        cy: float = 239.5,
    ) -> None:
        """
        Args:
            fx: Focal length in pixels (x-axis).
            fy: Focal length in pixels (y-axis).
            cx: Principal point x.
            cy: Principal point y.
        """
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy

    def lift(
        self,
        poses: List[PoseResult],
        depth_map: np.ndarray,
    ) -> List[np.ndarray]:
        """Back-project 2-D poses to 3-D.

        Args:
            poses: List of :class:`~vision.pose.human_pose_estimator.PoseResult`
                   with keypoints of shape ``(17, 3)`` – ``(x, y, visibility)``.
            depth_map: Float32 array of shape ``(H, W)`` with depth in metres.

        Returns:
            List of float32 arrays of shape ``(17, 3)`` with 3-D coordinates
            ``(X, Y, Z)`` in metres.
        """
        h, w = depth_map.shape[:2]
        results_3d: List[np.ndarray] = []

        for pose in poses:
            kps = pose.keypoints  # (17, 3) – (x, y, visibility)
            kps_3d = np.zeros((len(kps), 3), dtype=np.float32)

            for i, (u, v, vis) in enumerate(kps):
                ui, vi = int(np.clip(u, 0, w - 1)), int(np.clip(v, 0, h - 1))
                Z = float(depth_map[vi, ui])
                if Z <= 0 or not np.isfinite(Z):
                    kps_3d[i] = [0.0, 0.0, 0.0]
                else:
                    kps_3d[i, 0] = (u - self.cx) * Z / self.fx
                    kps_3d[i, 1] = (v - self.cy) * Z / self.fy
                    kps_3d[i, 2] = Z

            results_3d.append(kps_3d)

        return results_3d

    def compute_bone_lengths(self, pose_3d: np.ndarray) -> dict:
        """Compute anatomical bone lengths from a 3-D pose.

        Args:
            pose_3d: Float32 array of shape ``(17, 3)`` in metres.

        Returns:
            Dict mapping bone names to lengths in metres.
        """
        # COCO 17-keypoint skeleton connections
        connections = {
            "left_upper_arm": (5, 7),
            "left_forearm": (7, 9),
            "right_upper_arm": (6, 8),
            "right_forearm": (8, 10),
            "left_thigh": (11, 13),
            "left_shin": (13, 15),
            "right_thigh": (12, 14),
            "right_shin": (14, 16),
            "torso": (5, 11),
        }
        lengths = {}
        for name, (i, j) in connections.items():
            if i < len(pose_3d) and j < len(pose_3d):
                lengths[name] = float(np.linalg.norm(pose_3d[i] - pose_3d[j]))
        return lengths
