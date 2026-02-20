"""Semantic segmentation using DeepLabV3+ via torchvision."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# PASCAL VOC class names (21 classes including background)
VOC_CLASSES: List[str] = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
    "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
    "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor",
]


class SemanticSegmentor:
    """Semantic segmentor using DeepLabV3+ from *torchvision*.

    Performs per-pixel class labelling.  The default model is trained on
    PASCAL VOC (21 classes).

    Example::

        seg = SemanticSegmentor(backbone="resnet50", device="cuda")
        mask = seg.segment(image)           # (H, W) int array
        colored = seg.colorize(mask)        # (H, W, 3) BGR image
    """

    BACKBONES = {"resnet50", "resnet101", "mobilenet_v3_large"}

    def __init__(
        self,
        model_name: str = "deeplabv3plus",
        backbone: str = "resnet50",
        device: str = "cpu",
        input_size: Tuple[int, int] = (512, 512),
        num_classes: int = 21,
    ) -> None:
        """
        Args:
            model_name: Segmentation architecture (currently only deeplabv3+ is used).
            backbone: Feature extractor backbone.
            device: ``"cuda"`` or ``"cpu"``.
            input_size: ``(height, width)`` to resize input before inference.
            num_classes: Number of output classes.
        """
        if backbone not in self.BACKBONES:
            logger.warning("Unknown backbone '%s', using resnet50", backbone)
            backbone = "resnet50"

        self.model_name = model_name
        self.backbone = backbone
        self.device = device
        self.input_size = input_size
        self.num_classes = num_classes
        self._model = None
        self._transform = None

    def _load_model(self) -> None:
        """Lazily load the torchvision DeepLabV3 model."""
        try:
            import torch
            import torchvision.transforms as T  # type: ignore
            from torchvision.models.segmentation import (  # type: ignore
                deeplabv3_resnet50,
                deeplabv3_resnet101,
                deeplabv3_mobilenet_v3_large,
            )

            loaders = {
                "resnet50": deeplabv3_resnet50,
                "resnet101": deeplabv3_resnet101,
                "mobilenet_v3_large": deeplabv3_mobilenet_v3_large,
            }
            loader_fn = loaders[self.backbone]
            self._model = loader_fn(pretrained=True)
            self._model.to(self.device)
            self._model.eval()

            self._transform = T.Compose([
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            logger.info("Loaded DeepLabV3 (%s) on %s", self.backbone, self.device)
        except ImportError as exc:
            raise ImportError(
                "torch and torchvision are required for SemanticSegmentor. "
                "Install with: pip install torch torchvision"
            ) from exc

    def segment(self, image: np.ndarray) -> np.ndarray:
        """Produce a per-pixel class-label map for *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            Integer array of shape ``(H, W)`` with class IDs.
        """
        if self._model is None:
            self._load_model()

        try:
            import cv2
            import torch
            from PIL import Image as PILImage

            orig_h, orig_w = image.shape[:2]
            resized = cv2.resize(
                image[..., ::-1],  # BGR -> RGB
                (self.input_size[1], self.input_size[0]),
            )
            pil_img = PILImage.fromarray(resized)
            tensor = self._transform(pil_img).unsqueeze(0).to(self.device)  # (1,3,H,W)

            with torch.no_grad():
                output = self._model(tensor)["out"]  # (1, num_classes, H, W)

            pred = output.argmax(1).squeeze(0).cpu().numpy().astype(np.int32)
            # Resize back to original resolution
            pred_resized = cv2.resize(
                pred.astype(np.uint8),
                (orig_w, orig_h),
                interpolation=cv2.INTER_NEAREST,
            ).astype(np.int32)
            return pred_resized
        except Exception as exc:
            logger.error("SemanticSegmentor.segment failed: %s", exc)
            return np.zeros(image.shape[:2], dtype=np.int32)

    def get_class_name(self, class_id: int) -> str:
        """Return the class name for *class_id*."""
        if 0 <= class_id < len(VOC_CLASSES):
            return VOC_CLASSES[class_id]
        return f"class_{class_id}"

    def colorize(self, seg_map: np.ndarray) -> np.ndarray:
        """Convert a segmentation map to a coloured BGR image.

        Args:
            seg_map: Integer array of shape ``(H, W)``.

        Returns:
            BGR colour image of shape ``(H, W, 3)``.
        """
        palette = _voc_colormap(256)
        h, w = seg_map.shape[:2]
        rgb = palette[seg_map.clip(0, 255)]
        import cv2
        return cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)


def _voc_colormap(n: int) -> np.ndarray:
    """Generate VOC-style colour palette of *n* colours."""
    palette = np.zeros((n, 3), dtype=np.uint8)
    for i in range(n):
        r, g, b, c = 0, 0, 0, i
        for _ in range(8):
            r |= ((c >> 0) & 1) << (7 - _)
            g |= ((c >> 1) & 1) << (7 - _)
            b |= ((c >> 2) & 1) << (7 - _)
            c >>= 3
        palette[i] = [r, g, b]
    return palette
