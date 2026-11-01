"""Stereo depth estimator using OpenCV's SGBM disparity algorithm."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StereoCalibration:
    """Stereo camera calibration parameters.

    Attributes:
        fx: Focal length in pixels (x-axis).
        fy: Focal length in pixels (y-axis).
        cx: Principal point x.
        cy: Principal point y.
        baseline: Camera baseline distance in metres.
        R: Optional 3×3 rotation matrix between the two cameras.
        T: Optional 3-element translation vector between the two cameras.
    """

    fx: float
    fy: float
    cx: float
    cy: float
    baseline: float  # metres
    R: Optional[np.ndarray] = None
    T: Optional[np.ndarray] = None


class StereoDepthEstimator:
    """Estimate depth from a rectified stereo image pair.

    Uses OpenCV's Semi-Global Block Matching (SGBM) algorithm to compute
    a disparity map which is then converted to metric depth.

    Example::

        calib = StereoCalibration(fx=718.8, fy=718.8, cx=607.2, cy=185.2,
                                   baseline=0.54)
        est = StereoDepthEstimator(calibration=calib)
        depth = est.estimate(left_image, right_image)  # metres
    """

    def __init__(
        self,
        calibration: Optional[StereoCalibration] = None,
        num_disparities: int = 96,
        block_size: int = 11,
        min_disparity: int = 0,
    ) -> None:
        """
        Args:
            calibration: Stereo calibration parameters.  If ``None``, a
                         default calibration is used and depths will not
                         be metric.
            num_disparities: Number of disparity levels (must be divisible by 16).
            block_size: Matched block size (odd number ≥ 1).
            min_disparity: Minimum disparity (can be negative for wide baselines).
        """
        if calibration is None:
            calibration = StereoCalibration(
                fx=500.0, fy=500.0, cx=320.0, cy=240.0, baseline=0.1
            )
        self.calibration = calibration
        # Ensure num_disparities is divisible by 16
        self.num_disparities = max(16, (num_disparities // 16) * 16)
        self.block_size = block_size if block_size % 2 == 1 else block_size + 1
        self.min_disparity = min_disparity
        self._stereo = None  # lazy

    def _build_matcher(self):
        """Create the OpenCV SGBM matcher."""
        import cv2

        p1 = 8 * 3 * self.block_size ** 2
        p2 = 32 * 3 * self.block_size ** 2
        self._stereo = cv2.StereoSGBM_create(
            minDisparity=self.min_disparity,
            numDisparities=self.num_disparities,
            blockSize=self.block_size,
            P1=p1,
            P2=p2,
            disp12MaxDiff=1,
            uniquenessRatio=10,
            speckleWindowSize=100,
            speckleRange=32,
            preFilterCap=63,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
        )

    def compute_disparity(
        self, left: np.ndarray, right: np.ndarray
    ) -> np.ndarray:
        """Compute the disparity map from a stereo pair.

        Args:
            left: Left BGR image ``(H, W, 3)``.
            right: Right BGR image ``(H, W, 3)``.

        Returns:
            Float32 disparity map ``(H, W)``.
        """
        if self._stereo is None:
            self._build_matcher()

        import cv2

        left_g = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
        right_g = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)
        disp = self._stereo.compute(left_g, right_g).astype(np.float32) / 16.0
        disp[disp <= 0] = np.nan
        return disp

    def estimate(
        self, left: np.ndarray, right: np.ndarray
    ) -> np.ndarray:
        """Compute metric depth from a stereo image pair.

        Args:
            left: Left BGR image ``(H, W, 3)``.
            right: Right BGR image ``(H, W, 3)``.

        Returns:
            Float32 depth map ``(H, W)`` in metres.  Invalid pixels are 0.
        """
        try:
            disp = self.compute_disparity(left, right)
            depth = np.where(
                np.isnan(disp),
                0.0,
                (self.calibration.fx * self.calibration.baseline) / disp,
            ).astype(np.float32)
            return depth
        except Exception as exc:
            logger.error("StereoDepthEstimator.estimate failed: %s", exc)
            return np.zeros(left.shape[:2], dtype=np.float32)
