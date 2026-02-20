"""
Image segmentation module for the RAG7 perception system.

Provides semantic segmentation with a graceful mock fallback.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class Segmenter:
    """Semantic image segmenter using a PyTorch backbone.

    Returns per-pixel class masks along with class labels and confidence
    scores.  Falls back to a mock output when no model is loaded.

    Args:
        model_path: Optional path to a serialised segmentation model.
        device: Compute device (``"cpu"`` or ``"cuda"``).
    """

    DEFAULT_CLASSES = ["background", "floor", "wall", "obstacle", "robot", "human"]

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu",
    ) -> None:
        """Initialize the segmenter."""
        self._logger = logging.getLogger("rag7.perception.segmentation")
        self._device = device
        self._model: Optional[Any] = None

        if model_path is not None:
            self._try_load_model(model_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def segment(self, image: np.ndarray) -> Dict[str, Any]:
        """Segment an image into semantic regions.

        Args:
            image: RGB image as a numpy array of shape (H, W, C).

        Returns:
            Dictionary with:
                - ``masks``: numpy array of shape (num_classes, H, W).
                - ``labels``: list of class label strings.
                - ``scores``: list of confidence floats per class.
        """
        if image is None or image.size == 0:
            return {"masks": np.array([]), "labels": [], "scores": []}

        if self._model is not None and TORCH_AVAILABLE:
            try:
                return self._model_segment(image)
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("Segmentation inference failed: %s", exc)

        return self._mock_segment(image)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _mock_segment(self, image: np.ndarray) -> Dict[str, Any]:
        """Return mock segmentation output.

        Args:
            image: Input image (used for shape only).

        Returns:
            Mock segmentation dictionary.
        """
        h, w = image.shape[:2]
        num_classes = len(self.DEFAULT_CLASSES)
        masks = np.zeros((num_classes, h, w), dtype=np.float32)
        # Floor mask: bottom third of the image
        masks[1, h * 2 // 3 :, :] = 1.0
        # Wall mask: top half
        masks[2, : h // 2, :] = 1.0

        return {
            "masks": masks,
            "labels": list(self.DEFAULT_CLASSES),
            "scores": [0.95, 0.88, 0.75, 0.60, 0.50, 0.40],
        }

    def _model_segment(self, image: np.ndarray) -> Dict[str, Any]:
        """Run model-based segmentation.

        Args:
            image: Input image.

        Returns:
            Segmentation output dictionary.
        """
        import torch

        img = image.astype(np.float32) / 255.0
        tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(self._device)
        with torch.no_grad():
            output = self._model(tensor)
        # Placeholder parse; real parsing is model-specific
        return {"masks": np.array([]), "labels": [], "scores": []}

    def _try_load_model(self, path: str) -> None:
        """Attempt to load a segmentation model from disk."""
        if not TORCH_AVAILABLE:
            return
        try:
            import torch

            self._model = torch.load(path, map_location=self._device)
            self._model.eval()
            self._logger.info("Segmentation model loaded from '%s'.", path)
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Could not load segmentation model: %s", exc)
