"""YOLO-based object detector using the ultralytics library."""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

from vision.detection.detector import BaseDetector, DetectionResult

logger = logging.getLogger(__name__)


class YOLODetector(BaseDetector):
    """Object detector backed by YOLOv8 via the *ultralytics* package.

    Model weights are downloaded automatically on first use and cached by
    the ultralytics library.

    Example::

        detector = YOLODetector(model_size="yolov8n", device="cuda")
        results = detector.detect(image)
    """

    VALID_SIZES = {"yolov8n", "yolov8s", "yolov8m", "yolov8l", "yolov8x"}

    def __init__(
        self,
        model_size: str = "yolov8n",
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.45,
        device: str = "cpu",
        enable_tracking: bool = False,
        classes: Optional[List[int]] = None,
    ) -> None:
        """
        Args:
            model_size: YOLO variant, e.g. ``"yolov8n"``.
            confidence_threshold: Minimum detection score.
            nms_threshold: IoU threshold for NMS.
            device: ``"cuda"`` or ``"cpu"``.
            enable_tracking: Whether to use built-in ByteTrack tracker.
            classes: Optional list of class IDs to keep; ``None`` keeps all.
        """
        super().__init__(
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            device=device,
        )
        if model_size not in self.VALID_SIZES:
            logger.warning(
                "Unknown model size '%s'; defaulting to 'yolov8n'", model_size
            )
            model_size = "yolov8n"

        self.model_size = model_size
        self.enable_tracking = enable_tracking
        self.classes = classes
        self._model = None  # lazy

    # ------------------------------------------------------------------
    # Lazy loading
    # ------------------------------------------------------------------

    def _load_model(self):
        """Download / load the YOLO model on first use."""
        try:
            from ultralytics import YOLO  # type: ignore

            self._model = YOLO(f"{self.model_size}.pt")
            self._model.to(self.device)
            logger.info("Loaded %s on %s", self.model_size, self.device)
        except ImportError as exc:
            raise ImportError(
                "ultralytics is required for YOLODetector. "
                "Install it with: pip install ultralytics"
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """Run YOLO detection on *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of :class:`~vision.detection.detector.DetectionResult`.
        """
        if self._model is None:
            self._load_model()

        try:
            if self.enable_tracking:
                raw = self._model.track(
                    image,
                    conf=self.confidence_threshold,
                    iou=self.nms_threshold,
                    persist=True,
                    verbose=False,
                )
            else:
                raw = self._model(
                    image,
                    conf=self.confidence_threshold,
                    iou=self.nms_threshold,
                    classes=self.classes,
                    verbose=False,
                )
        except Exception as exc:
            logger.error("YOLODetector.detect failed: %s", exc)
            return []

        return self._parse_results(raw)

    def _parse_results(self, raw_results) -> List[DetectionResult]:
        """Convert ultralytics result objects to :class:`DetectionResult` list."""
        detections: List[DetectionResult] = []
        for result in raw_results:
            boxes = result.boxes
            if boxes is None:
                continue
            names = result.names

            for i in range(len(boxes)):
                try:
                    xyxy = boxes.xyxy[i].cpu().numpy().tolist()
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls_id = int(boxes.cls[i].cpu().numpy())
                    track_id = None
                    if boxes.id is not None:
                        track_id = int(boxes.id[i].cpu().numpy())

                    detections.append(
                        DetectionResult(
                            bbox=(xyxy[0], xyxy[1], xyxy[2], xyxy[3]),
                            class_name=names.get(cls_id, str(cls_id)),
                            class_id=cls_id,
                            confidence=conf,
                            track_id=track_id,
                        )
                    )
                except Exception as exc:  # pragma: no cover
                    logger.warning("Skipping malformed box: %s", exc)

        return detections
