"""Affordance detector: find graspable/placeable regions in a scene."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AffordanceRegion:
    """A region with a specific affordance.

    Attributes:
        affordance_type: E.g. ``"grasp"``, ``"place"``, ``"push"``.
        center: ``(x, y)`` pixel coordinates of the region centre.
        bbox: Bounding box ``(x1, y1, x2, y2)``.
        confidence: Affordance confidence score.
        object_class: Associated object class if known.
    """

    affordance_type: str
    center: Tuple[float, float]
    bbox: Tuple[float, float, float, float]
    confidence: float
    object_class: str = ""


class AffordanceDetector:
    """Detect object affordances (grasp points, placement surfaces, etc.).

    Uses a combination of:

    1. Object class priors (e.g. bottles are graspable at the body).
    2. Depth and edge information for surface detection.
    3. Free-space analysis for placement regions.

    Example::

        detector = AffordanceDetector()
        regions = detector.detect(image, detections)
    """

    # Class-specific grasp point offsets (as fraction of bbox height from top)
    _GRASP_OFFSETS: Dict[str, float] = {
        "bottle": 0.35,
        "cup": 0.4,
        "mug": 0.4,
        "bowl": 0.5,
        "tool": 0.3,
        "default": 0.45,
    }

    def __init__(self, min_confidence: float = 0.3) -> None:
        """
        Args:
            min_confidence: Minimum confidence to report an affordance region.
        """
        self.min_confidence = min_confidence

    def detect(
        self,
        image: np.ndarray,
        detections: list,
        depth_map: np.ndarray | None = None,
    ) -> List[AffordanceRegion]:
        """Detect affordance regions in *image*.

        Args:
            image: BGR numpy array.
            detections: List of detection results with ``bbox`` and
                        ``class_name`` attributes.
            depth_map: Optional depth map for surface analysis.

        Returns:
            List of :class:`AffordanceRegion`.
        """
        regions: List[AffordanceRegion] = []

        # Grasp affordances from detections
        for det in detections:
            grasp_regions = self._grasp_from_detection(det)
            regions.extend(grasp_regions)

        # Placement affordances from flat surfaces
        if depth_map is not None:
            place_regions = self._placement_regions(depth_map)
            regions.extend(place_regions)

        return [r for r in regions if r.confidence >= self.min_confidence]

    def _grasp_from_detection(self, det) -> List[AffordanceRegion]:
        """Generate grasp affordances from a single detection."""
        x1, y1, x2, y2 = det.bbox
        w = x2 - x1
        h = y2 - y1

        if w < 10 or h < 10:
            return []

        offset = self._GRASP_OFFSETS.get(det.class_name.lower(), self._GRASP_OFFSETS["default"])
        cx = x1 + w / 2
        cy = y1 + h * offset

        # Grasp box: horizontal strip at grasp height
        gw = w * 0.6
        gh = h * 0.2
        bbox = (cx - gw / 2, cy - gh / 2, cx + gw / 2, cy + gh / 2)

        return [
            AffordanceRegion(
                affordance_type="grasp",
                center=(cx, cy),
                bbox=bbox,
                confidence=float(det.confidence),
                object_class=det.class_name,
            )
        ]

    @staticmethod
    def _placement_regions(depth_map: np.ndarray) -> List[AffordanceRegion]:
        """Identify flat placement surfaces using depth planarity."""
        try:
            import cv2

            h, w = depth_map.shape[:2]
            # Normalise and threshold to find near-flat regions
            valid = depth_map > 0
            if not valid.any():
                return []

            # Sobel gradient as a proxy for planarity
            dm_norm = (depth_map - depth_map[valid].min())
            dm_norm = (dm_norm / (dm_norm.max() + 1e-8) * 255).astype(np.uint8)
            grad_x = cv2.Sobel(dm_norm, cv2.CV_32F, 1, 0, ksize=5)
            grad_y = cv2.Sobel(dm_norm, cv2.CV_32F, 0, 1, ksize=5)
            gradient = np.sqrt(grad_x ** 2 + grad_y ** 2)

            flat_mask = ((gradient < 5) & valid).astype(np.uint8)
            kernel = np.ones((15, 15), np.uint8)
            flat_mask = cv2.morphologyEx(flat_mask, cv2.MORPH_OPEN, kernel)

            contours, _ = cv2.findContours(
                flat_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            regions: List[AffordanceRegion] = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 2000:
                    continue
                rx, ry, rw, rh = cv2.boundingRect(cnt)
                cx, cy = rx + rw / 2, ry + rh / 2
                regions.append(
                    AffordanceRegion(
                        affordance_type="place",
                        center=(float(cx), float(cy)),
                        bbox=(float(rx), float(ry), float(rx + rw), float(ry + rh)),
                        confidence=min(1.0, area / (w * h) * 10),
                    )
                )
            return regions
        except Exception as exc:
            logger.error("_placement_regions failed: %s", exc)
            return []
