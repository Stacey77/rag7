"""Person-specific detector that filters YOLO detections to humans only."""

from __future__ import annotations

import logging
from typing import List

import numpy as np

from vision.detection.detector import DetectionResult
from vision.detection.yolo_detector import YOLODetector

logger = logging.getLogger(__name__)

# COCO person class ID
_PERSON_CLASS_ID = 0


class PersonDetector(YOLODetector):
    """Detects people only by restricting YOLO to the COCO person class.

    Example::

        detector = PersonDetector(device="cuda")
        people = detector.detect(image)
    """

    def __init__(
        self,
        model_size: str = "yolov8n",
        confidence_threshold: float = 0.5,
        device: str = "cpu",
    ) -> None:
        super().__init__(
            model_size=model_size,
            confidence_threshold=confidence_threshold,
            device=device,
            classes=[_PERSON_CLASS_ID],
        )

    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect all people in *image*.

        Returns only detections whose ``class_id`` is the COCO person class.
        """
        results = super().detect(image)
        return [r for r in results if r.class_id == _PERSON_CLASS_ID]
