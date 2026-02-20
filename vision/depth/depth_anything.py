"""Depth-Anything monocular depth estimator via HuggingFace."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from vision.depth.depth_estimator import DepthEstimator

logger = logging.getLogger(__name__)


class DepthAnythingEstimator(DepthEstimator):
    """Depth estimator using the *Depth Anything* model from HuggingFace.

    Produces metric or relative depth maps depending on the chosen variant.

    Example::

        est = DepthAnythingEstimator(device="cuda")
        depth = est.estimate(image)   # float32 (H, W) in metres or relative
    """

    DEFAULT_MODEL = "LiheYoung/depth-anything-base-hf"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "cpu",
        normalize: bool = False,
    ) -> None:
        """
        Args:
            model_name: HuggingFace model identifier.
            device: ``"cuda"`` or ``"cpu"``.
            normalize: Normalise output depth to ``[0, 1]``.
        """
        self.model_name = model_name
        self.device = device
        self.normalize = normalize
        self._model = None
        self._processor = None

    def _load_model(self) -> None:
        """Lazily load the Depth Anything model."""
        try:
            from transformers import (  # type: ignore
                AutoImageProcessor,
                AutoModelForDepthEstimation,
            )

            self._processor = AutoImageProcessor.from_pretrained(self.model_name)
            self._model = AutoModelForDepthEstimation.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()
            logger.info("Loaded Depth Anything '%s' on %s", self.model_name, self.device)
        except ImportError as exc:
            raise ImportError(
                "transformers is required for DepthAnythingEstimator. "
                "Install with: pip install transformers"
            ) from exc

    def estimate(self, image: np.ndarray) -> np.ndarray:
        """Estimate a depth map for *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            Float32 depth map of shape ``(H, W)``.
        """
        if self._model is None:
            self._load_model()

        try:
            import torch
            from PIL import Image as PILImage

            orig_h, orig_w = image.shape[:2]
            rgb = image[..., ::-1].copy()
            pil = PILImage.fromarray(rgb)

            inputs = self._processor(images=pil, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self._model(**inputs)
                predicted_depth = outputs.predicted_depth  # (1, H', W')

            depth = torch.nn.functional.interpolate(
                predicted_depth.unsqueeze(1),
                size=(orig_h, orig_w),
                mode="bicubic",
                align_corners=False,
            ).squeeze().cpu().numpy().astype(np.float32)

            if self.normalize:
                dmin, dmax = depth.min(), depth.max()
                if dmax > dmin:
                    depth = (depth - dmin) / (dmax - dmin)
                else:
                    depth = np.zeros_like(depth)
            return depth
        except Exception as exc:
            logger.error("DepthAnythingEstimator.estimate failed: %s", exc)
            h, w = image.shape[:2]
            return np.zeros((h, w), dtype=np.float32)
