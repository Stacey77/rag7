"""Image captioner using BLIP from HuggingFace."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class ImageCaptioner:
    """Generate natural-language captions for images using BLIP.

    Example::

        captioner = ImageCaptioner(device="cuda")
        caption = captioner.caption(image)
    """

    DEFAULT_MODEL = "Salesforce/blip-image-captioning-base"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "cpu",
        max_new_tokens: int = 64,
        num_beams: int = 4,
    ) -> None:
        """
        Args:
            model_name: HuggingFace BLIP model identifier.
            device: ``"cuda"`` or ``"cpu"``.
            max_new_tokens: Maximum tokens to generate.
            num_beams: Beam search width.
        """
        self.model_name = model_name
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.num_beams = num_beams
        self._model = None
        self._processor = None

    def _load(self) -> None:
        """Lazily load the BLIP captioning model."""
        try:
            from transformers import (  # type: ignore
                BlipForConditionalGeneration,
                BlipProcessor,
            )

            self._processor = BlipProcessor.from_pretrained(self.model_name)
            self._model = BlipForConditionalGeneration.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()
            logger.info("Loaded BLIP captioner '%s' on %s", self.model_name, self.device)
        except ImportError as exc:
            raise ImportError(
                "transformers is required for ImageCaptioner. "
                "Install with: pip install transformers"
            ) from exc

    def caption(self, image: np.ndarray, conditional_text: str = "") -> str:
        """Generate a caption for *image*.

        Args:
            image: BGR numpy array.
            conditional_text: Optional prefix for conditional captioning.

        Returns:
            Generated caption string.
        """
        if self._model is None:
            self._load()

        try:
            import torch
            from PIL import Image as PILImage

            rgb = image[..., ::-1].copy()
            pil = PILImage.fromarray(rgb)

            if conditional_text:
                inputs = self._processor(pil, conditional_text, return_tensors="pt").to(self.device)
            else:
                inputs = self._processor(pil, return_tensors="pt").to(self.device)

            with torch.no_grad():
                out = self._model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    num_beams=self.num_beams,
                )
            caption = self._processor.decode(out[0], skip_special_tokens=True).strip()
            return caption
        except Exception as exc:
            logger.error("ImageCaptioner.caption failed: %s", exc)
            return ""

    def caption_batch(self, images: list) -> list:
        """Caption a list of images.

        Args:
            images: List of BGR numpy arrays.

        Returns:
            List of caption strings.
        """
        return [self.caption(img) for img in images]
