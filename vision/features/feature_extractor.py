"""Feature extractor supporting classical and deep feature methods."""

from __future__ import annotations

import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract visual features using classical or deep methods.

    Classical methods (ORB, SIFT) return keypoints and binary/float
    descriptors.  The deep method uses a ResNet backbone to extract a
    global feature vector.

    Example::

        extractor = FeatureExtractor()
        kps, descs = extractor.extract(image, method="orb")
        global_feat = extractor.extract_deep(image)   # (2048,) float32
    """

    SUPPORTED_METHODS = ("orb", "sift", "akaze")

    def __init__(self, device: str = "cpu") -> None:
        self.device = device
        self._deep_model = None
        self._deep_transform = None

    def extract(
        self,
        image: np.ndarray,
        method: str = "orb",
        max_features: int = 500,
    ) -> Tuple[list, Optional[np.ndarray]]:
        """Extract keypoints and descriptors from *image*.

        Args:
            image: BGR numpy array.
            method: Feature type – one of ``"orb"``, ``"sift"``, ``"akaze"``.
            max_features: Maximum number of features to detect.

        Returns:
            Tuple of ``(keypoints, descriptors)`` where *keypoints* is a list
            of ``cv2.KeyPoint`` and *descriptors* is a float32/uint8 array of
            shape ``(N, D)`` or ``None`` if no features are found.
        """
        try:
            import cv2

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            if method == "orb":
                detector = cv2.ORB_create(nfeatures=max_features)
            elif method == "sift":
                detector = cv2.SIFT_create(nfeatures=max_features)
            elif method == "akaze":
                detector = cv2.AKAZE_create()
            else:
                logger.warning("Unknown method '%s'; using ORB", method)
                detector = cv2.ORB_create(nfeatures=max_features)

            kps, descs = detector.detectAndCompute(gray, None)
            return list(kps), descs
        except Exception as exc:
            logger.error("FeatureExtractor.extract failed: %s", exc)
            return [], None

    def extract_deep(self, image: np.ndarray) -> np.ndarray:
        """Extract a deep global feature vector using ResNet.

        Args:
            image: BGR numpy array.

        Returns:
            L2-normalised float32 array of shape ``(2048,)``.
        """
        if self._deep_model is None:
            self._load_deep_model()

        try:
            import torch

            rgb = image[..., ::-1].copy()
            tensor = self._deep_transform(rgb).unsqueeze(0).to(self.device)

            with torch.no_grad():
                feat = self._deep_model(tensor).squeeze().cpu().numpy()

            norm = np.linalg.norm(feat)
            if norm > 1e-8:
                feat /= norm
            return feat.astype(np.float32)
        except Exception as exc:
            logger.error("FeatureExtractor.extract_deep failed: %s", exc)
            return np.zeros(2048, dtype=np.float32)

    def _load_deep_model(self) -> None:
        """Lazily load ResNet-50 for deep feature extraction."""
        try:
            import torch
            import torch.nn as nn
            import torchvision.models as models
            import torchvision.transforms as T

            backbone = models.resnet50(pretrained=True)
            self._deep_model = nn.Sequential(*list(backbone.children())[:-1])
            self._deep_model.to(self.device)
            self._deep_model.eval()

            self._deep_transform = T.Compose([
                T.ToPILImage(),
                T.Resize(256),
                T.CenterCrop(224),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        except ImportError as exc:
            raise ImportError(
                "torch and torchvision are required for deep feature extraction."
            ) from exc
