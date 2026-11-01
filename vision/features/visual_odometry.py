"""Monocular visual odometry via feature tracking."""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class VisualOdometry:
    """Estimate camera motion from consecutive image frames.

    Uses Lucas-Kanade sparse optical flow to track ORB keypoints and the
    essential matrix for relative pose estimation.

    Example::

        vo = VisualOdometry(fx=718.8, fy=718.8, cx=607.2, cy=185.2)
        for frame in frames:
            R, t = vo.process_frame(frame)
    """

    def __init__(
        self,
        fx: float = 718.8,
        fy: float = 718.8,
        cx: float = 607.2,
        cy: float = 185.2,
        feature_method: str = "orb",
    ) -> None:
        """
        Args:
            fx: Focal length in pixels (x).
            fy: Focal length in pixels (y).
            cx: Principal point x.
            cy: Principal point y.
            feature_method: Feature detector type (``"orb"`` or ``"fast"``).
        """
        self.K = np.array(
            [[fx, 0, cx],
             [0, fy, cy],
             [0, 0, 1.0]],
            dtype=np.float64,
        )
        self.feature_method = feature_method
        self._prev_gray: Optional[np.ndarray] = None
        self._prev_pts: Optional[np.ndarray] = None
        self._trajectory: List[np.ndarray] = []  # list of 4×4 pose matrices
        self._current_pose = np.eye(4, dtype=np.float64)

    def process_frame(
        self, image: np.ndarray
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Estimate rotation and translation from the previous frame.

        Args:
            image: BGR numpy array.

        Returns:
            Tuple ``(R, t)`` where ``R`` is 3×3 and ``t`` is ``(3, 1)``
            (both float64).  Returns ``(None, None)`` for the first frame.
        """
        try:
            import cv2

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            if self._prev_gray is None:
                self._prev_gray = gray
                self._prev_pts = self._detect_features(gray)
                self._trajectory.append(self._current_pose.copy())
                return None, None

            # Track features with LK optical flow
            if self._prev_pts is None or len(self._prev_pts) < 8:
                self._prev_pts = self._detect_features(gray)
                self._prev_gray = gray
                return None, None

            curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(
                self._prev_gray, gray,
                self._prev_pts, None,
                winSize=(21, 21), maxLevel=3,
            )
            status = status.ravel().astype(bool)
            good_prev = self._prev_pts[status]
            good_curr = curr_pts[status]

            if len(good_prev) < 8:
                self._prev_gray = gray
                self._prev_pts = self._detect_features(gray)
                return None, None

            E, mask = cv2.findEssentialMat(
                good_curr, good_prev, self.K,
                method=cv2.RANSAC, prob=0.999, threshold=1.0,
            )
            if E is None:
                return None, None

            _, R, t, _ = cv2.recoverPose(E, good_curr, good_prev, self.K)

            # Update pose
            T = np.eye(4, dtype=np.float64)
            T[:3, :3] = R
            T[:3, 3] = t.ravel()
            self._current_pose = self._current_pose @ np.linalg.inv(T)
            self._trajectory.append(self._current_pose.copy())

            # Re-detect features periodically
            if len(good_curr) < 100:
                self._prev_pts = self._detect_features(gray)
            else:
                self._prev_pts = good_curr.reshape(-1, 1, 2)
            self._prev_gray = gray

            return R, t
        except Exception as exc:
            logger.error("VisualOdometry.process_frame failed: %s", exc)
            return None, None

    def _detect_features(self, gray: np.ndarray) -> np.ndarray:
        """Detect feature points in a grayscale image."""
        import cv2

        if self.feature_method == "fast":
            detector = cv2.FastFeatureDetector_create()
            kps = detector.detect(gray, None)
            pts = np.float32([kp.pt for kp in kps]).reshape(-1, 1, 2)
        else:
            orb = cv2.ORB_create(nfeatures=500)
            kps = orb.detect(gray, None)
            pts = np.float32([kp.pt for kp in kps]).reshape(-1, 1, 2)
        return pts

    def get_trajectory(self) -> np.ndarray:
        """Return the accumulated camera trajectory.

        Returns:
            Array of shape ``(N, 4, 4)`` with homogeneous pose matrices.
        """
        if not self._trajectory:
            return np.empty((0, 4, 4), dtype=np.float64)
        return np.stack(self._trajectory, axis=0)

    def reset(self) -> None:
        """Reset the odometry to an initial state."""
        self._prev_gray = None
        self._prev_pts = None
        self._trajectory.clear()
        self._current_pose = np.eye(4, dtype=np.float64)
