"""Camera intrinsics and projection utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CameraIntrinsics:
    """Camera intrinsic parameters.

    Attributes:
        fx: Focal length in pixels (x-axis).
        fy: Focal length in pixels (y-axis).
        cx: Principal point x.
        cy: Principal point y.
        width: Image width in pixels.
        height: Image height in pixels.
        dist_coeffs: Distortion coefficients (k1, k2, p1, p2[, k3]).
    """

    fx: float
    fy: float
    cx: float
    cy: float
    width: int = 640
    height: int = 480
    dist_coeffs: np.ndarray = field(
        default_factory=lambda: np.zeros(5, dtype=np.float32)
    )

    @property
    def K(self) -> np.ndarray:
        """3×3 camera matrix."""
        return np.array(
            [[self.fx, 0, self.cx],
             [0, self.fy, self.cy],
             [0, 0, 1.0]],
            dtype=np.float64,
        )

    @classmethod
    def from_fov(
        cls,
        hfov_deg: float,
        width: int,
        height: int,
    ) -> "CameraIntrinsics":
        """Create intrinsics from a horizontal field-of-view.

        Args:
            hfov_deg: Horizontal FOV in degrees.
            width: Image width.
            height: Image height.

        Returns:
            :class:`CameraIntrinsics` instance.
        """
        hfov_rad = np.deg2rad(hfov_deg)
        fx = (width / 2) / np.tan(hfov_rad / 2)
        fy = fx
        cx = width / 2.0
        cy = height / 2.0
        return cls(fx=fx, fy=fy, cx=cx, cy=cy, width=width, height=height)


def project_3d_to_2d(
    points_3d: np.ndarray,
    intrinsics: CameraIntrinsics,
    rotation: Optional[np.ndarray] = None,
    translation: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Project 3-D world points to 2-D image coordinates.

    Args:
        points_3d: Float array of shape ``(N, 3)`` in camera or world frame.
        intrinsics: Camera intrinsics.
        rotation: Optional 3×3 rotation matrix (world → camera).
        translation: Optional 3-element translation vector.

    Returns:
        Float32 array of shape ``(N, 2)`` with pixel coordinates.
    """
    pts = points_3d.astype(np.float64).copy()

    if rotation is not None and translation is not None:
        pts = (rotation @ pts.T).T + translation.ravel()

    # Guard against points behind camera
    valid = pts[:, 2] > 1e-8
    u = np.where(valid, pts[:, 0] / pts[:, 2] * intrinsics.fx + intrinsics.cx, 0.0)
    v = np.where(valid, pts[:, 1] / pts[:, 2] * intrinsics.fy + intrinsics.cy, 0.0)

    return np.stack([u, v], axis=1).astype(np.float32)


def backproject_2d_to_3d(
    points_2d: np.ndarray,
    depth: np.ndarray,
    intrinsics: CameraIntrinsics,
) -> np.ndarray:
    """Back-project 2-D pixel coordinates to 3-D using a depth map or values.

    Args:
        points_2d: Float array of shape ``(N, 2)`` with ``(u, v)`` coordinates.
        depth: Either a scalar, a 1-D array of length ``N``, or a 2-D depth map
               ``(H, W)`` from which depths are sampled.
        intrinsics: Camera intrinsics.

    Returns:
        Float32 array of shape ``(N, 3)`` with 3-D coordinates in metres.
    """
    pts = points_2d.astype(np.float64)
    if isinstance(depth, np.ndarray) and depth.ndim == 2:
        h, w = depth.shape[:2]
        us = np.clip(pts[:, 0].astype(int), 0, w - 1)
        vs = np.clip(pts[:, 1].astype(int), 0, h - 1)
        Z = depth[vs, us].astype(np.float64)
    else:
        Z = np.asarray(depth, dtype=np.float64).ravel()
        if Z.size == 1:
            Z = np.full(len(pts), Z.item())

    x = (pts[:, 0] - intrinsics.cx) * Z / intrinsics.fx
    y = (pts[:, 1] - intrinsics.cy) * Z / intrinsics.fy
    return np.stack([x, y, Z], axis=1).astype(np.float32)


def undistort_image(
    image: np.ndarray,
    intrinsics: CameraIntrinsics,
    balance: float = 0.0,
) -> np.ndarray:
    """Remove lens distortion from *image*.

    Args:
        image: BGR numpy array.
        intrinsics: Camera intrinsics including distortion coefficients.
        balance: Balance between full and cropped undistorted image (0–1).

    Returns:
        Undistorted BGR image.
    """
    try:
        import cv2

        h, w = image.shape[:2]
        new_K, roi = cv2.getOptimalNewCameraMatrix(
            intrinsics.K,
            intrinsics.dist_coeffs,
            (w, h),
            balance,
        )
        undistorted = cv2.undistort(
            image,
            intrinsics.K,
            intrinsics.dist_coeffs,
            None,
            new_K,
        )
        x, y, rw, rh = roi
        if rw > 0 and rh > 0:
            undistorted = undistorted[y:y + rh, x:x + rw]
        return undistorted
    except Exception as exc:
        logger.error("undistort_image failed: %s", exc)
        return image
