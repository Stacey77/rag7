"""Re-identification model for appearance-based tracking."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class ReIDModel:
    """Extract appearance features from object crops for re-identification.

    Uses a lightweight ResNet-based backbone for feature extraction.
    Features are L2-normalised before being returned.

    Example::

        reid = ReIDModel(device="cpu")
        feat = reid.extract(crop_image)           # (512,) float32
        dist = reid.cosine_distance(feat_a, feat_b)
    """

    EMBEDDING_DIM = 512

    def __init__(self, device: str = "cpu", embedding_dim: int = 512) -> None:
        """
        Args:
            device: ``"cuda"`` or ``"cpu"``.
            embedding_dim: Desired embedding dimensionality (used if a
                           projection head is applied).
        """
        self.device = device
        self.embedding_dim = embedding_dim
        self._model = None
        self._transform = None

    def _load_model(self) -> None:
        """Lazily load a pre-trained ResNet-18 backbone."""
        try:
            import torch
            import torch.nn as nn
            import torchvision.models as models
            import torchvision.transforms as T

            backbone = models.resnet18(pretrained=True)
            # Remove final classification layer; keep global average pool
            self._model = nn.Sequential(*list(backbone.children())[:-1])
            self._model.to(self.device)
            self._model.eval()

            self._transform = T.Compose([
                T.ToPILImage(),
                T.Resize((128, 64)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            logger.info("Loaded ReID model (ResNet-18) on %s", self.device)
        except ImportError as exc:
            raise ImportError(
                "torch and torchvision are required for ReIDModel. "
                "Install with: pip install torch torchvision"
            ) from exc

    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract a normalised appearance feature vector from *image*.

        Args:
            image: BGR crop of shape ``(H, W, 3)``.

        Returns:
            L2-normalised float32 array of shape ``(D,)`` where
            ``D`` is 512 for ResNet-18.
        """
        if self._model is None:
            self._load_model()

        try:
            import torch

            rgb = image[..., ::-1].copy()
            tensor = self._transform(rgb).unsqueeze(0).to(self.device)

            with torch.no_grad():
                feat = self._model(tensor).squeeze()  # (512,)

            feat_np = feat.cpu().numpy().astype(np.float32)
            norm = np.linalg.norm(feat_np)
            if norm > 1e-8:
                feat_np /= norm
            return feat_np
        except Exception as exc:
            logger.error("ReIDModel.extract failed: %s", exc)
            return np.zeros(self.EMBEDDING_DIM, dtype=np.float32)

    @staticmethod
    def cosine_distance(feat_a: np.ndarray, feat_b: np.ndarray) -> float:
        """Cosine distance between two feature vectors.

        Args:
            feat_a: Feature vector of shape ``(D,)``.
            feat_b: Feature vector of shape ``(D,)``.

        Returns:
            Distance in ``[0, 2]`` where 0 = identical, 2 = opposite.
        """
        norm_a = np.linalg.norm(feat_a)
        norm_b = np.linalg.norm(feat_b)
        if norm_a < 1e-8 or norm_b < 1e-8:
            return 1.0
        return float(1.0 - np.dot(feat_a, feat_b) / (norm_a * norm_b))

    def compare(self, crops: list, query_crop: np.ndarray) -> np.ndarray:
        """Rank a list of *crops* by similarity to *query_crop*.

        Args:
            crops: List of BGR images.
            query_crop: Query BGR image.

        Returns:
            Array of cosine distances corresponding to each crop.
        """
        query_feat = self.extract(query_crop)
        distances = np.array([
            self.cosine_distance(query_feat, self.extract(c)) for c in crops
        ])
        return distances
