"""Grasp point detector for robotic manipulation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GraspCandidate:
    """A candidate grasp configuration.

    Attributes:
        center: ``(x, y)`` pixel coordinates of the grasp centre.
        angle: Grasp orientation in radians.
        width: Estimated gripper width in pixels.
        quality: Score in ``[0, 1]`` indicating grasp quality.
        depth: Estimated depth (metres) if available.
    """

    center: Tuple[float, float]
    angle: float
    width: float
    quality: float
    depth: float = 0.0


class GraspDetector:
    """Estimate robotic grasp candidates from an RGB image.

    The default implementation uses a lightweight heuristic pipeline:
    edge-guided rectangle sampling combined with image gradient analysis.
    For production use, this can be replaced with a learned model such as
    GR-ConvNet.

    Example::

        detector = GraspDetector(num_candidates=10)
        grasps = detector.detect(image)
        best = max(grasps, key=lambda g: g.quality)
    """

    def __init__(
        self,
        num_candidates: int = 10,
        min_quality: float = 0.2,
    ) -> None:
        """
        Args:
            num_candidates: Maximum number of grasp candidates to return.
            min_quality: Minimum quality threshold.
        """
        self.num_candidates = num_candidates
        self.min_quality = min_quality

    def detect(
        self,
        image: np.ndarray,
        depth_map: np.ndarray | None = None,
        mask: np.ndarray | None = None,
    ) -> List[GraspCandidate]:
        """Estimate grasp candidates for objects in *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.
            depth_map: Optional depth map of shape ``(H, W)`` in metres.
            mask: Optional binary object mask to restrict the search region.

        Returns:
            List of :class:`GraspCandidate` sorted by descending quality.
        """
        try:
            import cv2  # type: ignore

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            if mask is not None:
                edges = cv2.bitwise_and(edges, edges, mask=mask.astype(np.uint8))

            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            candidates: List[GraspCandidate] = []
            for contour in contours:
                if len(contour) < 5:
                    continue
                rect = cv2.minAreaRect(contour)
                (cx, cy), (w, h), angle = rect
                if w < 10 or h < 10:
                    continue
                width = float(max(w, h))
                quality = self._score(gray, (cx, cy), angle, depth_map)
                if quality < self.min_quality:
                    continue
                depth = self._sample_depth(depth_map, cx, cy)
                candidates.append(
                    GraspCandidate(
                        center=(float(cx), float(cy)),
                        angle=float(np.deg2rad(angle)),
                        width=width,
                        quality=quality,
                        depth=depth,
                    )
                )

            candidates.sort(key=lambda g: g.quality, reverse=True)
            return candidates[: self.num_candidates]
        except Exception as exc:
            logger.error("GraspDetector.detect failed: %s", exc)
            return []

    def _score(
        self,
        gray: np.ndarray,
        center: Tuple[float, float],
        angle: float,
        depth_map: np.ndarray | None,
    ) -> float:
        """Heuristic quality score based on local gradient magnitude."""
        try:
            import cv2

            cx, cy = int(center[0]), int(center[1])
            h, w = gray.shape[:2]
            r = 16
            x1, y1 = max(0, cx - r), max(0, cy - r)
            x2, y2 = min(w, cx + r), min(h, cy + r)
            patch = gray[y1:y2, x1:x2].astype(np.float32)
            if patch.size == 0:
                return 0.0
            sobelx = cv2.Sobel(patch, cv2.CV_32F, 1, 0, ksize=3)
            sobely = cv2.Sobel(patch, cv2.CV_32F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
            score = float(np.mean(magnitude)) / 255.0
            return min(score, 1.0)
        except Exception:
            return 0.0

    @staticmethod
    def _sample_depth(
        depth_map: np.ndarray | None, cx: float, cy: float
    ) -> float:
        """Sample depth at pixel ``(cx, cy)``."""
        if depth_map is None:
            return 0.0
        h, w = depth_map.shape[:2]
        xi, yi = int(cx), int(cy)
        if 0 <= xi < w and 0 <= yi < h:
            return float(depth_map[yi, xi])
        return 0.0
