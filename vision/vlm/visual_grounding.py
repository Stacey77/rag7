"""Visual grounding: map text queries to image bounding boxes."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class VisualGrounding:
    """Map natural-language descriptions to image regions.

    Uses a sliding-window CLIP approach as the default backend.
    Can be replaced with GLIP/OWL-ViT for better accuracy.

    Example::

        grounder = VisualGrounding(device="cuda")
        boxes = grounder.ground(image, "the red cup on the table")
    """

    DEFAULT_OWLVIT_MODEL = "google/owlvit-base-patch32"

    def __init__(
        self,
        backend: str = "owlvit",
        device: str = "cpu",
        threshold: float = 0.1,
    ) -> None:
        """
        Args:
            backend: ``"owlvit"`` (recommended) or ``"clip_sliding"``.
            device: ``"cuda"`` or ``"cpu"``.
            threshold: Minimum score to return a box.
        """
        self.backend = backend
        self.device = device
        self.threshold = threshold
        self._model = None
        self._processor = None
        self._clip = None

    def _load_owlvit(self) -> None:
        """Lazily load OWL-ViT for open-vocabulary detection."""
        try:
            from transformers import OwlViTForObjectDetection, OwlViTProcessor  # type: ignore

            self._processor = OwlViTProcessor.from_pretrained(self.DEFAULT_OWLVIT_MODEL)
            self._model = OwlViTForObjectDetection.from_pretrained(self.DEFAULT_OWLVIT_MODEL)
            self._model.to(self.device)
            self._model.eval()
            logger.info("Loaded OWL-ViT on %s", self.device)
        except ImportError as exc:
            raise ImportError(
                "transformers is required for VisualGrounding (owlvit backend). "
                "Install with: pip install transformers"
            ) from exc

    def _load_clip(self) -> None:
        """Lazily load the CLIP interface for the sliding window backend."""
        from vision.vlm.clip_interface import CLIPInterface

        self._clip = CLIPInterface(device=self.device)

    def ground(
        self,
        image: np.ndarray,
        text: str,
    ) -> List[Dict[str, Any]]:
        """Ground *text* to bounding boxes in *image*.

        Args:
            image: BGR numpy array.
            text: Natural-language description.

        Returns:
            List of dicts with ``"bbox"`` ``(x1, y1, x2, y2)``,
            ``"score"`` (float), and ``"label"`` (str).
        """
        if self.backend == "owlvit":
            return self._ground_owlvit(image, text)
        return self._ground_clip(image, text)

    def _ground_owlvit(
        self,
        image: np.ndarray,
        text: str,
    ) -> List[Dict[str, Any]]:
        """Ground using OWL-ViT open-vocabulary detector."""
        if self._model is None:
            self._load_owlvit()

        try:
            import torch
            from PIL import Image as PILImage

            rgb = image[..., ::-1].copy()
            pil = PILImage.fromarray(rgb)
            texts = [[text]]  # list of queries

            inputs = self._processor(text=texts, images=pil, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self._model(**inputs)

            target_size = torch.tensor([[pil.height, pil.width]]).to(self.device)
            results = self._processor.post_process_object_detection(
                outputs=outputs, target_sizes=target_size, threshold=self.threshold
            )[0]

            boxes_out: List[Dict[str, Any]] = []
            for score, label, box in zip(
                results["scores"], results["labels"], results["boxes"]
            ):
                b = box.cpu().tolist()
                boxes_out.append(
                    {
                        "bbox": (b[0], b[1], b[2], b[3]),
                        "score": float(score.cpu()),
                        "label": text,
                    }
                )
            return sorted(boxes_out, key=lambda d: d["score"], reverse=True)
        except Exception as exc:
            logger.error("VisualGrounding._ground_owlvit failed: %s", exc)
            return []

    def _ground_clip(
        self,
        image: np.ndarray,
        text: str,
    ) -> List[Dict[str, Any]]:
        """Ground using sliding-window CLIP scoring."""
        if self._clip is None:
            self._load_clip()

        result = self._clip.find_object(image, text, stride=32)
        if result["score"] >= self.threshold:
            return [
                {
                    "bbox": result["region"],
                    "score": result["score"],
                    "label": text,
                }
            ]
        return []
