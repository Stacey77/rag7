"""Visual question answering using BLIP-2."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class VisualQA:
    """Answer questions about images using BLIP-2.

    Example::

        vqa = VisualQA(device="cuda")
        answer = vqa.answer(image, "What colour is the car?")
    """

    DEFAULT_MODEL = "Salesforce/blip2-opt-2.7b"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "cpu",
        max_new_tokens: int = 64,
    ) -> None:
        """
        Args:
            model_name: HuggingFace model identifier.
            device: ``"cuda"`` or ``"cpu"``.
            max_new_tokens: Maximum token budget for generated answer.
        """
        self.model_name = model_name
        self.device = device
        self.max_new_tokens = max_new_tokens
        self._model = None
        self._processor = None

    def _load(self) -> None:
        """Lazily load the BLIP-2 model and processor."""
        try:
            from transformers import Blip2ForConditionalGeneration, Blip2Processor  # type: ignore

            self._processor = Blip2Processor.from_pretrained(self.model_name)
            self._model = Blip2ForConditionalGeneration.from_pretrained(
                self.model_name, device_map=self.device
            )
            self._model.eval()
            logger.info("Loaded BLIP-2 '%s' on %s", self.model_name, self.device)
        except ImportError as exc:
            raise ImportError(
                "transformers is required for VisualQA. "
                "Install with: pip install transformers"
            ) from exc

    def answer(self, image: np.ndarray, question: str) -> str:
        """Answer *question* about *image*.

        Args:
            image: BGR numpy array.
            question: Natural-language question string.

        Returns:
            Generated answer string.
        """
        if self._model is None:
            self._load()

        try:
            import torch
            from PIL import Image as PILImage

            rgb = image[..., ::-1].copy()
            pil = PILImage.fromarray(rgb)
            prompt = f"Question: {question} Answer:"
            inputs = self._processor(images=pil, text=prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                generated_ids = self._model.generate(
                    **inputs, max_new_tokens=self.max_new_tokens
                )
            answer = self._processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0].strip()
            return answer
        except Exception as exc:
            logger.error("VisualQA.answer failed: %s", exc)
            return ""
