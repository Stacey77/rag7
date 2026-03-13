"""Base depth estimator and MiDaS-based monocular depth estimator."""

from __future__ import annotations

import abc
import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class DepthEstimator(abc.ABC):
    """Abstract base class for depth estimation."""

    @abc.abstractmethod
    def estimate(self, image: np.ndarray) -> np.ndarray:
        """Estimate a depth map for *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            Float32 depth map of shape ``(H, W)`` normalised to ``[0, 1]``
            unless the model produces metric depths.
        """


class MonocularDepthEstimator(DepthEstimator):
    """Monocular depth estimator using Intel MiDaS via *torch.hub*.

    Produces a relative depth map (larger values = closer).

    Example::

        estimator = MonocularDepthEstimator(model_name="midas", device="cuda")
        depth = estimator.estimate(image)   # shape (H, W), float32 in [0, 1]
    """

    MODEL_MAP = {
        "midas": ("intel-isl/MiDaS", "MiDaS"),
        "midas_small": ("intel-isl/MiDaS", "MiDaS_small"),
        "dpt_large": ("intel-isl/MiDaS", "DPT_Large"),
        "dpt_hybrid": ("intel-isl/MiDaS", "DPT_Hybrid"),
    }

    def __init__(
        self,
        model_name: str = "midas",
        device: str = "cpu",
        input_size: Tuple[int, int] = (384, 384),
        normalize: bool = True,
    ) -> None:
        """
        Args:
            model_name: One of ``"midas"``, ``"midas_small"``, ``"dpt_large"``,
                        ``"dpt_hybrid"``.
            device: ``"cuda"`` or ``"cpu"``.
            input_size: ``(height, width)`` to resize input.
            normalize: If ``True``, output is normalised to ``[0, 1]``.
        """
        if model_name not in self.MODEL_MAP:
            logger.warning("Unknown depth model '%s'; using 'midas'", model_name)
            model_name = "midas"

        self.model_name = model_name
        self.device = device
        self.input_size = input_size
        self.normalize = normalize
        self._model = None
        self._transform = None

    def _load_model(self) -> None:
        """Lazily load the MiDaS model from torch.hub."""
        try:
            import torch

            repo, model_key = self.MODEL_MAP[self.model_name]
            self._model = torch.hub.load(repo, model_key, pretrained=True)
            self._model.to(self.device)
            self._model.eval()

            midas_transforms = torch.hub.load(repo, "transforms")
            if model_key in ("DPT_Large", "DPT_Hybrid"):
                self._transform = midas_transforms.dpt_transform
            else:
                self._transform = midas_transforms.small_transform
            logger.info("Loaded MiDaS '%s' on %s", model_key, self.device)
        except ImportError as exc:
            raise ImportError(
                "torch is required for MonocularDepthEstimator. "
                "Install with: pip install torch"
            ) from exc

    def estimate(self, image: np.ndarray) -> np.ndarray:
        """Compute a depth map for *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            Float32 depth map of shape ``(H, W)``.
        """
        if self._model is None:
            self._load_model()

        try:
            import cv2
            import torch

            orig_h, orig_w = image.shape[:2]
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            input_batch = self._transform(rgb).to(self.device)

            with torch.no_grad():
                pred = self._model(input_batch)
                pred = torch.nn.functional.interpolate(
                    pred.unsqueeze(1),
                    size=(orig_h, orig_w),
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()

            depth = pred.cpu().numpy().astype(np.float32)

            if self.normalize:
                dmin, dmax = depth.min(), depth.max()
                if dmax > dmin:
                    depth = (depth - dmin) / (dmax - dmin)
                else:
                    depth = np.zeros_like(depth)
            return depth
        except Exception as exc:
            logger.error("MonocularDepthEstimator.estimate failed: %s", exc)
            h, w = image.shape[:2]
            return np.zeros((h, w), dtype=np.float32)
