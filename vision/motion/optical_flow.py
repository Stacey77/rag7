"""Dense and sparse optical flow computation."""

from __future__ import annotations

import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class OpticalFlow:
    """Compute dense and sparse optical flow between consecutive frames.

    Example::

        of = OpticalFlow()
        flow = of.compute_dense(frame1, frame2)     # (H, W, 2)
        pts2 = of.compute_sparse(frame1, frame2, pts)   # (N, 2)
    """

    def __init__(self) -> None:
        # LK parameters
        self._lk_params = dict(
            winSize=(21, 21),
            maxLevel=3,
            criteria=(3, 30, 0.01),  # TERM_CRITERIA_EPS + TERM_CRITERIA_COUNT
        )

    def compute_dense(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        pyr_scale: float = 0.5,
        levels: int = 3,
        winsize: int = 15,
        iterations: int = 3,
    ) -> np.ndarray:
        """Compute dense Farneback optical flow.

        Args:
            frame1: First BGR frame.
            frame2: Second BGR frame.
            pyr_scale: Scale factor for image pyramid.
            levels: Number of pyramid levels.
            winsize: Averaging window size.
            iterations: Algorithm iterations at each pyramid level.

        Returns:
            Float32 flow field of shape ``(H, W, 2)`` with ``(dx, dy)`` offsets.
        """
        try:
            import cv2

            g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(
                g1, g2, None,
                pyr_scale=pyr_scale,
                levels=levels,
                winsize=winsize,
                iterations=iterations,
                poly_n=5,
                poly_sigma=1.1,
                flags=0,
            )
            return flow  # (H, W, 2)
        except Exception as exc:
            logger.error("OpticalFlow.compute_dense failed: %s", exc)
            h, w = frame1.shape[:2]
            return np.zeros((h, w, 2), dtype=np.float32)

    def compute_sparse(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        points: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Track sparse feature points using Lucas-Kanade optical flow.

        Args:
            frame1: First BGR frame.
            frame2: Second BGR frame.
            points: Array of shape ``(N, 2)`` with ``(x, y)`` coordinates.

        Returns:
            Tuple of:
            - ``new_points``: Array ``(N, 2)`` of tracked positions.
            - ``status``: Boolean array ``(N,)`` – ``True`` if tracked.
        """
        try:
            import cv2

            g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            pts = points.reshape(-1, 1, 2).astype(np.float32)
            new_pts, status, _ = cv2.calcOpticalFlowPyrLK(
                g1, g2, pts, None, **self._lk_params
            )
            new_pts = new_pts.reshape(-1, 2)
            status = status.ravel().astype(bool)
            return new_pts, status
        except Exception as exc:
            logger.error("OpticalFlow.compute_sparse failed: %s", exc)
            return points.copy(), np.zeros(len(points), dtype=bool)

    @staticmethod
    def flow_to_rgb(flow: np.ndarray) -> np.ndarray:
        """Visualise a flow field as an HSV-encoded BGR image.

        Args:
            flow: Float32 array of shape ``(H, W, 2)``.

        Returns:
            BGR image of shape ``(H, W, 3)`` suitable for display.
        """
        import cv2

        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv = np.zeros((*flow.shape[:2], 3), dtype=np.uint8)
        hsv[..., 0] = angle * 180 / np.pi / 2  # hue = direction
        hsv[..., 1] = 255
        hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
