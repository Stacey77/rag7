"""CLIP interface for zero-shot classification and visual search."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class CLIPInterface:
    """Provides image-text alignment using CLIP.

    Supports zero-shot classification, image-text similarity scoring,
    and crude region-based visual search.

    Example::

        clip = CLIPInterface(device="cuda")
        scores = clip.classify(image, ["cat", "dog", "car"])
        emb = clip.encode_image(image)
        score = clip.find_object(image, "red cup")["score"]
    """

    DEFAULT_MODEL = "openai/clip-vit-base-patch32"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            model_name: HuggingFace CLIP model identifier.
            device: ``"cuda"`` or ``"cpu"``.
        """
        self.model_name = model_name
        self.device = device
        self._model = None
        self._processor = None

    def _load(self) -> None:
        """Lazily load the CLIP model."""
        try:
            from transformers import CLIPModel, CLIPProcessor  # type: ignore

            self._processor = CLIPProcessor.from_pretrained(self.model_name)
            self._model = CLIPModel.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()
            logger.info("Loaded CLIP '%s' on %s", self.model_name, self.device)
        except ImportError as exc:
            raise ImportError(
                "transformers is required for CLIPInterface. "
                "Install with: pip install transformers"
            ) from exc

    def encode_image(self, image: np.ndarray) -> np.ndarray:
        """Encode an image into a CLIP embedding.

        Args:
            image: BGR numpy array.

        Returns:
            L2-normalised float32 array of shape ``(D,)``.
        """
        if self._model is None:
            self._load()
        try:
            import torch
            from PIL import Image as PILImage

            rgb = image[..., ::-1].copy()
            pil = PILImage.fromarray(rgb)
            inputs = self._processor(images=pil, return_tensors="pt").to(self.device)
            with torch.no_grad():
                feat = self._model.get_image_features(**inputs)
                feat = feat / feat.norm(dim=-1, keepdim=True)
            return feat.squeeze().cpu().numpy().astype(np.float32)
        except Exception as exc:
            logger.error("CLIPInterface.encode_image failed: %s", exc)
            return np.zeros(512, dtype=np.float32)

    def encode_text(self, text: str) -> np.ndarray:
        """Encode a text string into a CLIP embedding.

        Args:
            text: Query string.

        Returns:
            L2-normalised float32 array of shape ``(D,)``.
        """
        if self._model is None:
            self._load()
        try:
            import torch

            inputs = self._processor(text=[text], return_tensors="pt", padding=True).to(self.device)
            with torch.no_grad():
                feat = self._model.get_text_features(**inputs)
                feat = feat / feat.norm(dim=-1, keepdim=True)
            return feat.squeeze().cpu().numpy().astype(np.float32)
        except Exception as exc:
            logger.error("CLIPInterface.encode_text failed: %s", exc)
            return np.zeros(512, dtype=np.float32)

    def classify(self, image: np.ndarray, text_labels: List[str]) -> np.ndarray:
        """Zero-shot classify *image* against *text_labels*.

        Args:
            image: BGR numpy array.
            text_labels: List of candidate class descriptions.

        Returns:
            Float32 probability array of shape ``(len(text_labels),)`` that
            sums to 1.
        """
        if self._model is None:
            self._load()
        try:
            import torch
            from PIL import Image as PILImage

            rgb = image[..., ::-1].copy()
            pil = PILImage.fromarray(rgb)
            inputs = self._processor(
                text=text_labels,
                images=pil,
                return_tensors="pt",
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                out = self._model(**inputs)
                logits = out.logits_per_image  # (1, num_labels)
                probs = logits.softmax(dim=-1).squeeze()

            return probs.cpu().numpy().astype(np.float32)
        except Exception as exc:
            logger.error("CLIPInterface.classify failed: %s", exc)
            return np.ones(len(text_labels), dtype=np.float32) / len(text_labels)

    def find_object(
        self,
        image: np.ndarray,
        query: str,
        stride: int = 64,
    ) -> Dict[str, Any]:
        """Search for a described object by sliding a window over the image.

        Args:
            image: BGR numpy array.
            query: Natural-language description.
            stride: Window stride in pixels.

        Returns:
            Dict with ``"score"`` (float), ``"region"`` (bbox tuple), and
            ``"query"`` (str).
        """
        # Compute global score first as a fast-path
        global_scores = self.classify(image, [query, "background"])
        global_score = float(global_scores[0])

        h, w = image.shape[:2]
        best_score = global_score
        best_region = (0, 0, w, h)

        # Simple sliding window at half resolution
        win_h, win_w = h // 2, w // 2
        for y in range(0, h - win_h + 1, stride):
            for x in range(0, w - win_w + 1, stride):
                crop = image[y:y + win_h, x:x + win_w]
                scores = self.classify(crop, [query, "background"])
                s = float(scores[0])
                if s > best_score:
                    best_score = s
                    best_region = (x, y, x + win_w, y + win_h)

        return {"score": best_score, "region": best_region, "query": query}

    def answer_question(self, image: np.ndarray, question: str) -> str:
        """Answer a visual question using CLIP similarity scoring.

        This is a lightweight heuristic: it formulates candidate answers
        (Yes/No) and scores them.

        Args:
            image: BGR numpy array.
            question: Natural-language question.

        Returns:
            ``"Yes"`` or ``"No"`` based on CLIP scores.
        """
        labels = [f"yes, {question}", f"no, {question}"]
        scores = self.classify(image, labels)
        return "Yes" if scores[0] > scores[1] else "No"
