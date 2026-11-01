"""Model loader with registry and local cache support."""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default cache directory
_DEFAULT_CACHE = Path.home() / ".cache" / "vision_models"

# Registry of known models: name -> {"url": str, "file": str, "type": str}
MODEL_REGISTRY: Dict[str, Dict[str, str]] = {
    "yolov8n": {
        "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
        "file": "yolov8n.pt",
        "type": "yolo",
    },
    "yolov8s": {
        "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt",
        "file": "yolov8s.pt",
        "type": "yolo",
    },
    "midas": {
        "url": "",  # loaded via torch.hub
        "file": "",
        "type": "depth",
    },
    "clip-vit-base": {
        "url": "openai/clip-vit-base-patch32",
        "file": "",
        "type": "clip",
    },
    "detr-resnet-50": {
        "url": "facebook/detr-resnet-50",
        "file": "",
        "type": "detection",
    },
    "blip-caption": {
        "url": "Salesforce/blip-image-captioning-base",
        "file": "",
        "type": "caption",
    },
    "depth-anything-base": {
        "url": "LiheYoung/depth-anything-base-hf",
        "file": "",
        "type": "depth",
    },
    "sam-vit-base": {
        "url": "facebook/sam-vit-base",
        "file": "",
        "type": "segmentation",
    },
}


class ModelLoader:
    """Load, cache, and manage vision models.

    Example::

        loader = ModelLoader(cache_dir="~/.cache/my_models")
        loader.list_available_models()
        model = loader.load_model("clip-vit-base", device="cpu")
    """

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        """
        Args:
            cache_dir: Directory for storing downloaded model files.
                       Defaults to ``~/.cache/vision_models``.
        """
        self.cache_dir = Path(cache_dir or _DEFAULT_CACHE).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._loaded: Dict[str, Any] = {}

    def list_available_models(self) -> List[str]:
        """Return the list of registered model names."""
        return list(MODEL_REGISTRY.keys())

    def load_model(self, model_name: str, device: str = "cpu") -> Any:
        """Load a registered model, downloading it if necessary.

        Args:
            model_name: A key from :data:`MODEL_REGISTRY`.
            device: ``"cuda"`` or ``"cpu"``.

        Returns:
            Loaded model object.
        """
        cache_key = f"{model_name}_{device}"
        if cache_key in self._loaded:
            return self._loaded[cache_key]

        if model_name not in MODEL_REGISTRY:
            raise ValueError(
                f"Unknown model '{model_name}'. "
                f"Available: {self.list_available_models()}"
            )

        info = MODEL_REGISTRY[model_name]
        model_type = info["type"]

        if info.get("file"):
            self.download_if_needed(model_name)

        model = self._instantiate(model_name, info, device)
        self._loaded[cache_key] = model
        return model

    def _instantiate(self, name: str, info: dict, device: str) -> Any:
        """Instantiate a model from registry info."""
        model_type = info["type"]
        url = info.get("url", "")

        try:
            if model_type == "yolo":
                from ultralytics import YOLO  # type: ignore

                path = self.cache_dir / info["file"]
                if path.exists():
                    return YOLO(str(path))
                return YOLO(info["file"])

            if model_type == "clip":
                from transformers import CLIPModel, CLIPProcessor  # type: ignore

                model = CLIPModel.from_pretrained(url)
                model.to(device).eval()
                return model

            if model_type == "detection" and "detr" in name:
                from transformers import DetrForObjectDetection  # type: ignore

                model = DetrForObjectDetection.from_pretrained(url)
                model.to(device).eval()
                return model

            if model_type == "caption":
                from transformers import BlipForConditionalGeneration  # type: ignore

                model = BlipForConditionalGeneration.from_pretrained(url)
                model.to(device).eval()
                return model

            if model_type == "depth" and "depth-anything" in name:
                from transformers import AutoModelForDepthEstimation  # type: ignore

                model = AutoModelForDepthEstimation.from_pretrained(url)
                model.to(device).eval()
                return model

            if model_type == "depth":
                import torch

                model = torch.hub.load("intel-isl/MiDaS", "MiDaS", pretrained=True)
                model.to(device).eval()
                return model

            if model_type == "segmentation":
                from transformers import SamModel  # type: ignore

                model = SamModel.from_pretrained(url)
                model.to(device).eval()
                return model

            raise ValueError(f"Cannot instantiate model type '{model_type}'")
        except ImportError as exc:
            raise ImportError(
                f"Required package missing for model '{name}': {exc}"
            ) from exc

    def download_if_needed(self, model_name: str) -> Path:
        """Download a model file if it is not already cached.

        Args:
            model_name: Registry key.

        Returns:
            Local path to the model file.
        """
        info = MODEL_REGISTRY[model_name]
        filename = info.get("file", "")
        if not filename:
            return self.cache_dir

        dest = self.cache_dir / filename
        if dest.exists():
            logger.info("Model '%s' already cached at %s", model_name, dest)
            return dest

        url = info.get("url", "")
        if not url:
            raise FileNotFoundError(f"No URL registered for model '{model_name}'")

        logger.info("Downloading '%s' from %s …", model_name, url)
        try:
            import urllib.request

            urllib.request.urlretrieve(url, dest)
            logger.info("Saved to %s", dest)
        except Exception as exc:
            logger.error("Download failed: %s", exc)
            raise
        return dest

    def cache_model(self, model: Any, path: str) -> None:
        """Save a PyTorch model's state dict to *path*.

        Args:
            model: PyTorch model with a ``state_dict()`` method.
            path: Destination file path (e.g. ``"model.pt"``).
        """
        try:
            import torch

            torch.save(model.state_dict(), path)
            logger.info("Model cached at %s", path)
        except Exception as exc:
            logger.error("cache_model failed: %s", exc)
            raise

    def get_file_hash(self, path: str, algorithm: str = "sha256") -> str:
        """Compute a hex digest for a file (integrity checking).

        Args:
            path: File path.
            algorithm: Hash algorithm name.

        Returns:
            Hex digest string.
        """
        h = hashlib.new(algorithm)
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
