"""Base detector class and shared data structures."""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Represents a single detected object.

    Attributes:
        bbox: Bounding box in ``(x1, y1, x2, y2)`` pixel coordinates.
        class_name: Human-readable class label.
        class_id: Integer class index.
        confidence: Detection confidence in ``[0, 1]``.
        track_id: Optional tracking identifier assigned by a tracker.
        mask: Optional binary instance mask of shape ``(H, W)``.
        keypoints: Optional keypoint array of shape ``(N, 2)`` or ``(N, 3)``.
    """

    bbox: Tuple[float, float, float, float]
    class_name: str
    class_id: int
    confidence: float
    track_id: Optional[int] = None
    mask: Optional[np.ndarray] = None
    keypoints: Optional[np.ndarray] = None
    metadata: dict = field(default_factory=dict)

    @property
    def area(self) -> float:
        """Bounding-box area in pixels²."""
        x1, y1, x2, y2 = self.bbox
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)

    @property
    def center(self) -> Tuple[float, float]:
        """Centre ``(cx, cy)`` of the bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return {
            "bbox": list(self.bbox),
            "class_name": self.class_name,
            "class_id": self.class_id,
            "confidence": self.confidence,
            "track_id": self.track_id,
        }


class BaseDetector(abc.ABC):
    """Abstract base class for all object detectors.

    Subclasses must implement :meth:`detect`.  Common preprocessing and
    non-maximum suppression utilities are provided here.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.45,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            confidence_threshold: Minimum score to retain a detection.
            nms_threshold: IoU threshold used during NMS.
            device: ``"cuda"`` or ``"cpu"``.
        """
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.device = device

    @abc.abstractmethod
    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """Run detection on *image* and return a list of results.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of :class:`DetectionResult`.
        """

    def preprocess(self, image: np.ndarray, target_size: Tuple[int, int] = (640, 640)) -> np.ndarray:
        """Resize *image* to *target_size* and convert to float32 in ``[0, 1]``.

        Args:
            image: Input BGR numpy array.
            target_size: ``(width, height)`` tuple.

        Returns:
            Float32 numpy array of shape ``(H, W, 3)`` normalised to ``[0, 1]``.
        """
        import cv2  # type: ignore

        resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
        return resized.astype(np.float32) / 255.0

    @staticmethod
    def nms(
        boxes: np.ndarray,
        scores: np.ndarray,
        iou_threshold: float = 0.45,
    ) -> List[int]:
        """Apply non-maximum suppression.

        Args:
            boxes: Array of shape ``(N, 4)`` in ``(x1, y1, x2, y2)`` format.
            scores: Confidence scores of shape ``(N,)``.
            iou_threshold: IoU threshold above which overlapping boxes are suppressed.

        Returns:
            List of indices of kept boxes.
        """
        if len(boxes) == 0:
            return []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep: List[int] = []
        while order.size > 0:
            i = int(order[0])
            keep.append(i)
            if order.size == 1:
                break

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h

            iou = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(iou <= iou_threshold)[0]
            order = order[inds + 1]

        return keep
