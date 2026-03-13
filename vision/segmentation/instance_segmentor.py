"""Instance segmentation using Mask R-CNN from torchvision."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# COCO class names for Mask R-CNN
COCO_INSTANCE_CLASSES: List[str] = [
    "__background__", "person", "bicycle", "car", "motorcycle", "airplane",
    "bus", "train", "truck", "boat", "traffic light", "fire hydrant",
    "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse",
    "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork",
    "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven",
    "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
    "teddy bear", "hair drier", "toothbrush",
]


@dataclass
class InstanceMask:
    """A single instance segmentation result.

    Attributes:
        mask: Binary mask of shape ``(H, W)``.
        class_name: Predicted class label.
        class_id: Integer class index.
        score: Confidence score in ``[0, 1]``.
        bbox: Bounding box ``(x1, y1, x2, y2)``.
    """

    mask: np.ndarray
    class_name: str
    class_id: int
    score: float
    bbox: Tuple[float, float, float, float]


class InstanceSegmentor:
    """Instance segmentor using Mask R-CNN from *torchvision*.

    Example::

        seg = InstanceSegmentor(score_threshold=0.7, device="cuda")
        instances = seg.segment(image)
        for inst in instances:
            print(inst.class_name, inst.score)
    """

    def __init__(
        self,
        score_threshold: float = 0.5,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            score_threshold: Minimum score to retain a predicted instance.
            device: ``"cuda"`` or ``"cpu"``.
        """
        self.score_threshold = score_threshold
        self.device = device
        self._model = None
        self._transform = None

    def _load_model(self) -> None:
        """Lazily load the Mask R-CNN model."""
        try:
            import torch
            import torchvision.transforms as T
            from torchvision.models.detection import (  # type: ignore
                maskrcnn_resnet50_fpn,
                MaskRCNN_ResNet50_FPN_Weights,
            )

            weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT
            self._model = maskrcnn_resnet50_fpn(weights=weights)
            self._model.to(self.device)
            self._model.eval()
            self._transform = T.ToTensor()
            logger.info("Loaded Mask R-CNN on %s", self.device)
        except ImportError as exc:
            raise ImportError(
                "torch and torchvision are required for InstanceSegmentor. "
                "Install with: pip install torch torchvision"
            ) from exc

    def segment(self, image: np.ndarray) -> List[InstanceMask]:
        """Segment object instances in *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of :class:`InstanceMask` sorted by descending score.
        """
        if self._model is None:
            self._load_model()

        try:
            import torch

            rgb = image[..., ::-1].copy()
            tensor = self._transform(rgb).to(self.device)

            with torch.no_grad():
                outputs = self._model([tensor])[0]

            results: List[InstanceMask] = []
            boxes = outputs["boxes"].cpu().numpy()
            labels = outputs["labels"].cpu().numpy()
            scores = outputs["scores"].cpu().numpy()
            masks = outputs["masks"].cpu().numpy()  # (N, 1, H, W)

            for i, score in enumerate(scores):
                if score < self.score_threshold:
                    continue
                cls_id = int(labels[i])
                cls_name = (
                    COCO_INSTANCE_CLASSES[cls_id]
                    if cls_id < len(COCO_INSTANCE_CLASSES)
                    else str(cls_id)
                )
                binary_mask = (masks[i, 0] > 0.5).astype(np.uint8)
                b = boxes[i].tolist()
                results.append(
                    InstanceMask(
                        mask=binary_mask,
                        class_name=cls_name,
                        class_id=cls_id,
                        score=float(score),
                        bbox=(b[0], b[1], b[2], b[3]),
                    )
                )
            return sorted(results, key=lambda r: r.score, reverse=True)
        except Exception as exc:
            logger.error("InstanceSegmentor.segment failed: %s", exc)
            return []
