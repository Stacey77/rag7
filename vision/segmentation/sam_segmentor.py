"""Segment Anything Model (SAM) segmentor."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class SAMSegmentor:
    """Segmentor powered by Meta's Segment Anything Model (SAM).

    Supports three modes of interaction:

    - **Point prompts**: :meth:`segment_with_points`
    - **Box prompts**: :meth:`segment_with_box`
    - **Automatic mask generation**: :meth:`segment_everything`

    The implementation falls back to the HuggingFace *transformers* SAM
    interface if the standalone ``segment-anything`` package is unavailable.

    Example::

        sam = SAMSegmentor(device="cuda")
        masks = sam.segment_with_points(image, points=[(320, 240)])
    """

    HF_MODEL = "facebook/sam-vit-base"

    def __init__(
        self,
        model_type: str = "vit_b",
        checkpoint: Optional[str] = None,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            model_type: SAM model variant – ``"vit_b"``, ``"vit_l"``, ``"vit_h"``.
            checkpoint: Optional path to a local SAM checkpoint file.
            device: ``"cuda"`` or ``"cpu"``.
        """
        self.model_type = model_type
        self.checkpoint = checkpoint
        self.device = device
        self._predictor = None  # standalone SAM predictor
        self._hf_model = None   # HuggingFace SAM model
        self._hf_processor = None
        self._use_hf = False

    # ------------------------------------------------------------------
    # Lazy loading helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Attempt to load standalone SAM; fall back to HuggingFace."""
        try:
            from segment_anything import SamPredictor, sam_model_registry  # type: ignore

            if self.checkpoint is None:
                raise FileNotFoundError("No SAM checkpoint provided; trying HuggingFace")
            sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint)
            sam.to(self.device)
            self._predictor = SamPredictor(sam)
            logger.info("Loaded standalone SAM (%s)", self.model_type)
        except (ImportError, FileNotFoundError, KeyError):
            self._load_hf()

    def _load_hf(self) -> None:
        """Load SAM from HuggingFace Transformers."""
        try:
            from transformers import SamModel, SamProcessor  # type: ignore

            self._hf_processor = SamProcessor.from_pretrained(self.HF_MODEL)
            self._hf_model = SamModel.from_pretrained(self.HF_MODEL)
            self._hf_model.to(self.device)
            self._hf_model.eval()
            self._use_hf = True
            logger.info("Loaded HuggingFace SAM (%s)", self.HF_MODEL)
        except ImportError as exc:
            raise ImportError(
                "Install 'segment-anything' or 'transformers' for SAMSegmentor."
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def segment_with_points(
        self,
        image: np.ndarray,
        points: List[Tuple[int, int]],
        point_labels: Optional[List[int]] = None,
    ) -> List[np.ndarray]:
        """Segment objects near the given point prompts.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.
            points: List of ``(x, y)`` pixel coordinates.
            point_labels: Per-point labels (1=foreground, 0=background).
                          Defaults to all foreground.

        Returns:
            List of binary masks of shape ``(H, W)``.
        """
        if self._predictor is None and self._hf_model is None:
            self._load()

        if point_labels is None:
            point_labels = [1] * len(points)

        try:
            if not self._use_hf:
                return self._sam_predict_points(image, points, point_labels)
            return self._hf_predict_points(image, points, point_labels)
        except Exception as exc:
            logger.error("SAMSegmentor.segment_with_points failed: %s", exc)
            return []

    def segment_with_box(
        self,
        image: np.ndarray,
        box: Tuple[int, int, int, int],
    ) -> List[np.ndarray]:
        """Segment the object inside *box*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.
            box: Bounding box ``(x1, y1, x2, y2)``.

        Returns:
            List of binary masks of shape ``(H, W)``.
        """
        if self._predictor is None and self._hf_model is None:
            self._load()

        try:
            if not self._use_hf:
                return self._sam_predict_box(image, box)
            return self._hf_predict_box(image, box)
        except Exception as exc:
            logger.error("SAMSegmentor.segment_with_box failed: %s", exc)
            return []

    def segment_everything(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Automatically segment all objects in *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of dicts with ``"segmentation"`` (binary mask) and
            ``"area"`` keys, sorted by descending area.
        """
        if self._predictor is None and self._hf_model is None:
            self._load()

        try:
            if not self._use_hf:
                return self._sam_everything(image)
            return self._hf_everything(image)
        except Exception as exc:
            logger.error("SAMSegmentor.segment_everything failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Standalone SAM helpers
    # ------------------------------------------------------------------

    def _sam_predict_points(self, image, points, labels):
        import numpy as np

        rgb = image[..., ::-1].copy()
        self._predictor.set_image(rgb)
        pts = np.array(points, dtype=np.float32)
        lbs = np.array(labels, dtype=np.int32)
        masks, _, _ = self._predictor.predict(
            point_coords=pts, point_labels=lbs, multimask_output=True
        )
        return [m.astype(np.uint8) for m in masks]

    def _sam_predict_box(self, image, box):
        import numpy as np

        rgb = image[..., ::-1].copy()
        self._predictor.set_image(rgb)
        masks, _, _ = self._predictor.predict(
            box=np.array(box, dtype=np.float32), multimask_output=False
        )
        return [m.astype(np.uint8) for m in masks]

    def _sam_everything(self, image):
        from segment_anything import SamAutomaticMaskGenerator  # type: ignore

        rgb = image[..., ::-1].copy()
        gen = SamAutomaticMaskGenerator(self._predictor.model)
        return gen.generate(rgb)

    # ------------------------------------------------------------------
    # HuggingFace SAM helpers
    # ------------------------------------------------------------------

    def _hf_predict_points(self, image, points, labels):
        import torch
        from PIL import Image as PILImage

        rgb = image[..., ::-1].copy()
        pil = PILImage.fromarray(rgb)
        inputs = self._hf_processor(
            images=pil,
            input_points=[points],
            input_labels=[labels],
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self._hf_model(**inputs)

        masks = self._hf_processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(),
            inputs["original_sizes"].cpu(),
            inputs["reshaped_input_sizes"].cpu(),
        )[0][0]
        return [masks[i].numpy().astype(np.uint8) for i in range(masks.shape[0])]

    def _hf_predict_box(self, image, box):
        import torch
        from PIL import Image as PILImage

        rgb = image[..., ::-1].copy()
        pil = PILImage.fromarray(rgb)
        inputs = self._hf_processor(
            images=pil,
            input_boxes=[[list(box)]],
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self._hf_model(**inputs)

        masks = self._hf_processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(),
            inputs["original_sizes"].cpu(),
            inputs["reshaped_input_sizes"].cpu(),
        )[0][0]
        return [masks[0].numpy().astype(np.uint8)]

    def _hf_everything(self, image):
        """Approximate 'segment everything' using a grid of point prompts."""
        h, w = image.shape[:2]
        step = 64
        grid_points = [
            (x, y)
            for y in range(step // 2, h, step)
            for x in range(step // 2, w, step)
        ]
        masks = self._hf_predict_points(image, grid_points, [1] * len(grid_points))
        results = []
        for m in masks:
            area = int(m.sum())
            if area > 0:
                results.append({"segmentation": m, "area": area})
        return sorted(results, key=lambda r: r["area"], reverse=True)
