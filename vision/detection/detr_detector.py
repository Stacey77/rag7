"""DETR-based object detector using HuggingFace Transformers."""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

from vision.detection.detector import BaseDetector, DetectionResult

logger = logging.getLogger(__name__)

# COCO label list used by the pretrained DETR checkpoint
COCO_CLASSES = [
    "N/A", "person", "bicycle", "car", "motorcycle", "airplane", "bus",
    "train", "truck", "boat", "traffic light", "fire hydrant", "N/A",
    "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse",
    "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "N/A",
    "backpack", "umbrella", "N/A", "N/A", "handbag", "tie", "suitcase",
    "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
    "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
    "N/A", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana",
    "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
    "donut", "cake", "chair", "couch", "potted plant", "bed", "N/A",
    "dining table", "N/A", "N/A", "toilet", "N/A", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster",
    "sink", "refrigerator", "N/A", "book", "clock", "vase", "scissors",
    "teddy bear", "hair drier", "toothbrush",
]


class DETRDetector(BaseDetector):
    """Object detector backed by Facebook's DETR (DEtection TRansformer).

    Uses ``facebook/detr-resnet-50`` from HuggingFace by default.

    Example::

        detector = DETRDetector(threshold=0.7)
        detections = detector.detect(image)
    """

    DEFAULT_MODEL = "facebook/detr-resnet-50"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        threshold: float = 0.5,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            model_name: HuggingFace model identifier.
            threshold: Minimum logit probability to keep a detection.
            device: ``"cuda"`` or ``"cpu"``.
        """
        super().__init__(confidence_threshold=threshold, device=device)
        self.model_name = model_name
        self.threshold = threshold
        self._model = None
        self._processor = None

    def _load_model(self) -> None:
        """Lazily load the DETR model and feature extractor."""
        try:
            from transformers import (  # type: ignore
                DetrForObjectDetection,
                DetrImageProcessor,
            )
            import torch  # type: ignore

            self._processor = DetrImageProcessor.from_pretrained(self.model_name)
            self._model = DetrForObjectDetection.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()
            logger.info("Loaded DETR model '%s' on %s", self.model_name, self.device)
        except ImportError as exc:
            raise ImportError(
                "transformers and torch are required for DETRDetector. "
                "Install with: pip install transformers torch"
            ) from exc

    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """Run DETR detection on *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of :class:`~vision.detection.detector.DetectionResult`.
        """
        if self._model is None:
            self._load_model()

        try:
            import torch
            from PIL import Image as PILImage

            rgb = image[..., ::-1].copy()
            pil_img = PILImage.fromarray(rgb)
            inputs = self._processor(images=pil_img, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self._model(**inputs)

            target_sizes = torch.tensor([pil_img.size[::-1]]).to(self.device)
            results = self._processor.post_process_object_detection(
                outputs, threshold=self.threshold, target_sizes=target_sizes
            )[0]

            detections: List[DetectionResult] = []
            for score, label, box in zip(
                results["scores"], results["labels"], results["boxes"]
            ):
                s = float(score.cpu())
                l = int(label.cpu())
                b = box.cpu().tolist()
                class_name = COCO_CLASSES[l] if l < len(COCO_CLASSES) else str(l)
                detections.append(
                    DetectionResult(
                        bbox=(b[0], b[1], b[2], b[3]),
                        class_name=class_name,
                        class_id=l,
                        confidence=s,
                    )
                )
            return detections
        except Exception as exc:
            logger.error("DETRDetector.detect failed: %s", exc)
            return []
