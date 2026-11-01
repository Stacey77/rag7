"""Image denoising utilities."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class Denoiser:
    """Apply various image denoising algorithms.

    Example::

        denoiser = Denoiser()
        clean = denoiser.denoise(noisy_image, method="nlm")
    """

    SUPPORTED_METHODS = ("gaussian", "bilateral", "nlm", "median")

    def denoise(
        self,
        image: np.ndarray,
        method: str = "bilateral",
        **kwargs,
    ) -> np.ndarray:
        """Denoise *image* using the selected method.

        Args:
            image: BGR numpy array.
            method: One of ``"gaussian"``, ``"bilateral"``, ``"nlm"``,
                    ``"median"``.
            **kwargs: Method-specific parameters passed to the underlying
                      function.

        Returns:
            Denoised BGR numpy array.
        """
        if method not in self.SUPPORTED_METHODS:
            logger.warning("Unknown denoise method '%s'; using bilateral", method)
            method = "bilateral"

        dispatcher = {
            "gaussian": self._gaussian,
            "bilateral": self._bilateral,
            "nlm": self._nlm,
            "median": self._median,
        }
        try:
            return dispatcher[method](image, **kwargs)
        except Exception as exc:
            logger.error("Denoiser.denoise(%s) failed: %s", method, exc)
            return image

    @staticmethod
    def _gaussian(image: np.ndarray, ksize: int = 5, sigma: float = 0) -> np.ndarray:
        """Gaussian blur denoising."""
        import cv2
        ksize = ksize if ksize % 2 == 1 else ksize + 1
        return cv2.GaussianBlur(image, (ksize, ksize), sigma)

    @staticmethod
    def _bilateral(
        image: np.ndarray,
        d: int = 9,
        sigma_color: float = 75.0,
        sigma_space: float = 75.0,
    ) -> np.ndarray:
        """Bilateral filter – edge-preserving noise reduction."""
        import cv2
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

    @staticmethod
    def _nlm(
        image: np.ndarray,
        h: float = 10.0,
        template_window: int = 7,
        search_window: int = 21,
    ) -> np.ndarray:
        """Non-local means denoising."""
        import cv2
        return cv2.fastNlMeansDenoisingColored(
            image, None, h, h, template_window, search_window
        )

    @staticmethod
    def _median(image: np.ndarray, ksize: int = 5) -> np.ndarray:
        """Median filter – removes salt-and-pepper noise."""
        import cv2
        ksize = ksize if ksize % 2 == 1 else ksize + 1
        return cv2.medianBlur(image, ksize)

    def denoise_batch(
        self,
        images: list,
        method: str = "bilateral",
        **kwargs,
    ) -> list:
        """Denoise a list of images.

        Args:
            images: List of BGR numpy arrays.
            method: Denoising method.
            **kwargs: Forwarded to :meth:`denoise`.

        Returns:
            List of denoised images.
        """
        return [self.denoise(img, method=method, **kwargs) for img in images]
