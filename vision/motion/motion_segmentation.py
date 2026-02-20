"""Segment moving objects from a static or slowly-moving background."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class MotionSegmentor:
    """Segment moving regions in a video stream.

    Uses OpenCV's background subtractor (MOG2) by default.
    Also exposes a flow-based segmentation method.

    Example::

        seg = MotionSegmentor()
        mask = seg.segment(frame)   # binary (H, W) uint8
    """

    def __init__(
        self,
        method: str = "mog2",
        history: int = 500,
        var_threshold: float = 16.0,
        detect_shadows: bool = False,
        flow_threshold: float = 2.0,
    ) -> None:
        """
        Args:
            method: ``"mog2"`` (GMM) or ``"knn"`` or ``"flow"``.
            history: Number of frames for background model.
            var_threshold: Variance threshold for MOG2/KNN.
            detect_shadows: Whether to detect and mark shadows.
            flow_threshold: Minimum flow magnitude for the flow-based method.
        """
        self.method = method
        self.history = history
        self.var_threshold = var_threshold
        self.detect_shadows = detect_shadows
        self.flow_threshold = flow_threshold
        self._bg_subtractor = None
        self._prev_gray: Optional[np.ndarray] = None

    def _build_subtractor(self):
        """Lazily build the background subtractor."""
        import cv2

        if self.method == "knn":
            self._bg_subtractor = cv2.createBackgroundSubtractorKNN(
                history=self.history,
                dist2Threshold=self.var_threshold ** 2,
                detectShadows=self.detect_shadows,
            )
        else:
            self._bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=self.history,
                varThreshold=self.var_threshold,
                detectShadows=self.detect_shadows,
            )

    def segment(self, frame: np.ndarray) -> np.ndarray:
        """Produce a binary motion mask for *frame*.

        Args:
            frame: BGR numpy array.

        Returns:
            Binary uint8 mask of shape ``(H, W)`` where 255 = motion.
        """
        try:
            import cv2

            if self.method == "flow":
                return self._segment_flow(frame)

            if self._bg_subtractor is None:
                self._build_subtractor()

            fg_mask = self._bg_subtractor.apply(frame)
            # Clean up noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            # Binarise (remove shadow pixels if detectShadows=True)
            _, binary = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
            return binary
        except Exception as exc:
            logger.error("MotionSegmentor.segment failed: %s", exc)
            return np.zeros(frame.shape[:2], dtype=np.uint8)

    def _segment_flow(self, frame: np.ndarray) -> np.ndarray:
        """Segment motion using dense optical flow."""
        import cv2

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self._prev_gray is None:
            self._prev_gray = gray
            return np.zeros(gray.shape, dtype=np.uint8)

        flow = cv2.calcOpticalFlowFarneback(
            self._prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.1, 0
        )
        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        mask = (magnitude > self.flow_threshold).astype(np.uint8) * 255
        self._prev_gray = gray
        return mask

    def reset(self) -> None:
        """Reset the background model."""
        self._bg_subtractor = None
        self._prev_gray = None
