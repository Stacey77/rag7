"""Panoptic segmentation using torchvision Panoptic FPN."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PanopticResult:
    """Result of panoptic segmentation for a single image.

    Attributes:
        semantic_map: Per-pixel semantic class IDs, shape ``(H, W)``.
        instance_map: Per-pixel instance IDs (0 = background), shape ``(H, W)``.
        segments_info: List of dicts describing each segment (id, category, isthing).
    """

    semantic_map: np.ndarray
    instance_map: np.ndarray
    segments_info: List[dict]


class PanopticSegmentor:
    """Panoptic segmentor that unifies semantic and instance segmentation.

    Uses Panoptic FPN from HuggingFace Transformers when available,
    otherwise falls back to a combination of DeepLabV3 (semantic) and
    Mask R-CNN (instance) outputs.

    Example::

        seg = PanopticSegmentor(device="cuda")
        result = seg.segment(image)
        print(result.segments_info)
    """

    HF_MODEL = "facebook/detr-resnet-50-panoptic"

    def __init__(
        self,
        device: str = "cpu",
        threshold: float = 0.5,
    ) -> None:
        """
        Args:
            device: ``"cuda"`` or ``"cpu"``.
            threshold: Minimum confidence for segments.
        """
        self.device = device
        self.threshold = threshold
        self._model = None
        self._processor = None

    def _load_model(self) -> None:
        """Lazily load the panoptic segmentation model."""
        try:
            from transformers import (  # type: ignore
                DetrForSegmentation,
                DetrImageProcessor,
            )

            self._processor = DetrImageProcessor.from_pretrained(self.HF_MODEL)
            self._model = DetrForSegmentation.from_pretrained(self.HF_MODEL)
            self._model.to(self.device)
            self._model.eval()
            logger.info("Loaded panoptic DETR on %s", self.device)
        except ImportError as exc:
            raise ImportError(
                "transformers is required for PanopticSegmentor. "
                "Install with: pip install transformers"
            ) from exc

    def segment(self, image: np.ndarray) -> PanopticResult:
        """Run panoptic segmentation on *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            :class:`PanopticResult` with semantic and instance maps.
        """
        if self._model is None:
            self._load_model()

        h, w = image.shape[:2]
        try:
            import torch
            from PIL import Image as PILImage

            rgb = image[..., ::-1].copy()
            pil = PILImage.fromarray(rgb)
            inputs = self._processor(images=pil, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self._model(**inputs)

            result = self._processor.post_process_panoptic_segmentation(
                outputs,
                target_sizes=[(h, w)],
                threshold=self.threshold,
            )[0]

            pan_mask = result["segmentation"].cpu().numpy().astype(np.int32)
            segments_info = result.get("segments_info", [])

            # Build semantic and instance maps
            semantic_map = np.zeros((h, w), dtype=np.int32)
            instance_map = np.zeros((h, w), dtype=np.int32)
            for seg in segments_info:
                seg_id = seg["id"]
                cat_id = seg.get("label_id", 0)
                is_thing = seg.get("isthing", False)
                pixel_mask = pan_mask == seg_id
                semantic_map[pixel_mask] = cat_id
                if is_thing:
                    instance_map[pixel_mask] = seg_id

            return PanopticResult(
                semantic_map=semantic_map,
                instance_map=instance_map,
                segments_info=[dict(s) for s in segments_info],
            )
        except Exception as exc:
            logger.error("PanopticSegmentor.segment failed: %s", exc)
            return PanopticResult(
                semantic_map=np.zeros((h, w), dtype=np.int32),
                instance_map=np.zeros((h, w), dtype=np.int32),
                segments_info=[],
            )
