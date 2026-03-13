"""Super-resolution: upscale images using classical or deep methods."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class SuperResolution:
    """Upscale images using bicubic interpolation or a deep SR model.

    The ``"bicubic"`` backend requires only OpenCV.  The ``"esrgan"`` backend
    requires the ``basicsr`` or ``realesrgan`` package.

    Example::

        sr = SuperResolution(backend="bicubic")
        hires = sr.upscale(image, scale=4)
    """

    def __init__(
        self,
        backend: str = "bicubic",
        device: str = "cpu",
    ) -> None:
        """
        Args:
            backend: ``"bicubic"`` or ``"esrgan"``.
            device: Compute device for deep SR model.
        """
        self.backend = backend
        self.device = device
        self._model = None

    def upscale(self, image: np.ndarray, scale: int = 2) -> np.ndarray:
        """Upscale *image* by *scale* factor.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.
            scale: Upscaling factor (2 or 4).

        Returns:
            Upscaled BGR image of shape ``(H*scale, W*scale, 3)``.
        """
        if self.backend == "esrgan":
            return self._upscale_esrgan(image, scale)
        return self._upscale_bicubic(image, scale)

    @staticmethod
    def _upscale_bicubic(image: np.ndarray, scale: int) -> np.ndarray:
        """Bicubic interpolation upscaling."""
        import cv2
        h, w = image.shape[:2]
        return cv2.resize(
            image, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC
        )

    def _upscale_esrgan(self, image: np.ndarray, scale: int) -> np.ndarray:
        """Real-ESRGAN upscaling (requires ``realesrgan`` package)."""
        if self._model is None:
            self._load_esrgan(scale)

        try:
            output, _ = self._model.enhance(image, outscale=scale)
            return output
        except Exception as exc:
            logger.error("ESRGAN upscale failed: %s; falling back to bicubic", exc)
            return self._upscale_bicubic(image, scale)

    def _load_esrgan(self, scale: int) -> None:
        """Lazily load Real-ESRGAN model."""
        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet  # type: ignore
            from realesrgan import RealESRGANer  # type: ignore

            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=scale,
            )
            self._model = RealESRGANer(
                scale=scale,
                model_path=None,
                model=model,
                tile=0,
                half=False,
                device=self.device,
            )
            logger.info("Loaded Real-ESRGAN on %s", self.device)
        except ImportError as exc:
            raise ImportError(
                "realesrgan and basicsr are required for ESRGAN backend. "
                "Install with: pip install realesrgan basicsr"
            ) from exc

    def upscale_batch(self, images: list, scale: int = 2) -> list:
        """Upscale a list of images.

        Args:
            images: List of BGR numpy arrays.
            scale: Upscaling factor.

        Returns:
            List of upscaled images.
        """
        return [self.upscale(img, scale=scale) for img in images]
