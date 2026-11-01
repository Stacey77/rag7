"""Detection sub-package."""

from vision.detection.detector import BaseDetector, DetectionResult
from vision.detection.yolo_detector import YOLODetector
from vision.detection.detr_detector import DETRDetector
from vision.detection.person_detector import PersonDetector
from vision.detection.hand_detector import HandDetector
from vision.detection.grasp_detector import GraspDetector

__all__ = [
    "BaseDetector",
    "DetectionResult",
    "YOLODetector",
    "DETRDetector",
    "PersonDetector",
    "HandDetector",
    "GraspDetector",
]
