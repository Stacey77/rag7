"""Point cloud generation from depth maps and stereo images."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CameraIntrinsicsSimple:
    """Minimal camera intrinsics for point cloud generation."""

    fx: float
    fy: float
    cx: float
    cy: float


class PointCloudGenerator:
    """Generate 3-D point clouds from depth maps or stereo images.

    Example::

        gen = PointCloudGenerator()
        intrinsics = CameraIntrinsicsSimple(fx=525, fy=525, cx=319.5, cy=239.5)
        pc = gen.generate_from_depth(depth_map, intrinsics)   # (N, 3)
    """

    def generate_from_depth(
        self,
        depth_map: np.ndarray,
        intrinsics: CameraIntrinsicsSimple,
        rgb: Optional[np.ndarray] = None,
        max_depth: float = 10.0,
    ) -> np.ndarray:
        """Back-project a depth map into a 3-D point cloud.

        Args:
            depth_map: Float32 array of shape ``(H, W)`` with depth in metres.
                       Zero or NaN values are treated as invalid.
            intrinsics: Camera intrinsic parameters.
            rgb: Optional RGB image of shape ``(H, W, 3)`` for coloured clouds.
            max_depth: Points with depth > *max_depth* are discarded.

        Returns:
            If *rgb* is ``None``: float32 array of shape ``(N, 3)`` (x, y, z).
            If *rgb* is given: float32 array of shape ``(N, 6)`` (x, y, z, r, g, b).
        """
        h, w = depth_map.shape[:2]
        us, vs = np.meshgrid(np.arange(w), np.arange(h))

        valid = (depth_map > 0) & (depth_map <= max_depth) & np.isfinite(depth_map)
        z = depth_map[valid].astype(np.float32)
        u = us[valid].astype(np.float32)
        v = vs[valid].astype(np.float32)

        x = (u - intrinsics.cx) * z / intrinsics.fx
        y = (v - intrinsics.cy) * z / intrinsics.fy
        xyz = np.stack([x, y, z], axis=1)  # (N, 3)

        if rgb is not None:
            colours = rgb[valid].astype(np.float32) / 255.0
            return np.concatenate([xyz, colours], axis=1)

        return xyz

    def generate_from_stereo(
        self,
        left: np.ndarray,
        right: np.ndarray,
        calibration,
    ) -> np.ndarray:
        """Generate a point cloud from a rectified stereo pair.

        Args:
            left: Left BGR image ``(H, W, 3)``.
            right: Right BGR image ``(H, W, 3)``.
            calibration: :class:`~vision.depth.stereo_depth.StereoCalibration`.

        Returns:
            Float32 array of shape ``(N, 3)``.
        """
        from vision.depth.stereo_depth import StereoDepthEstimator

        estimator = StereoDepthEstimator(calibration=calibration)
        depth_map = estimator.estimate(left, right)
        intrinsics = CameraIntrinsicsSimple(
            fx=calibration.fx,
            fy=calibration.fy,
            cx=calibration.cx,
            cy=calibration.cy,
        )
        rgb_left = left[..., ::-1].copy()
        return self.generate_from_depth(depth_map, intrinsics, rgb=rgb_left)

    @staticmethod
    def filter_outliers(
        pointcloud: np.ndarray,
        nb_neighbors: int = 20,
        std_ratio: float = 2.0,
    ) -> np.ndarray:
        """Remove statistical outliers from a point cloud.

        Uses the mean distance to *nb_neighbors* nearest neighbours.
        Points with a distance exceeding ``mean + std_ratio * std`` are removed.

        Args:
            pointcloud: Float32 array of shape ``(N, 3)`` or ``(N, 6)``.
            nb_neighbors: Number of neighbours to consider.
            std_ratio: Threshold multiplier.

        Returns:
            Filtered point cloud of shape ``(M, K)`` where ``M ≤ N``.
        """
        if len(pointcloud) == 0:
            return pointcloud

        try:
            from sklearn.neighbors import NearestNeighbors  # type: ignore

            xyz = pointcloud[:, :3]
            nbrs = NearestNeighbors(n_neighbors=nb_neighbors + 1).fit(xyz)
            distances, _ = nbrs.kneighbors(xyz)
            mean_dists = distances[:, 1:].mean(axis=1)  # exclude self
            threshold = mean_dists.mean() + std_ratio * mean_dists.std()
            mask = mean_dists < threshold
            return pointcloud[mask]
        except ImportError:
            logger.warning(
                "scikit-learn not installed; skipping outlier filter."
            )
            return pointcloud
        except Exception as exc:
            logger.error("filter_outliers failed: %s", exc)
            return pointcloud

    @staticmethod
    def to_open3d(pointcloud: np.ndarray):
        """Convert numpy point cloud to an ``open3d.geometry.PointCloud``.

        Args:
            pointcloud: Float32 array of shape ``(N, 3)`` or ``(N, 6)``.

        Returns:
            ``open3d.geometry.PointCloud`` object.
        """
        try:
            import open3d as o3d  # type: ignore

            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(pointcloud[:, :3])
            if pointcloud.shape[1] >= 6:
                pcd.colors = o3d.utility.Vector3dVector(pointcloud[:, 3:6])
            return pcd
        except ImportError as exc:
            raise ImportError(
                "open3d is required for to_open3d. "
                "Install with: pip install open3d"
            ) from exc
