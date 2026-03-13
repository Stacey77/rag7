"""Image enhancement utilities."""

from __future__ import annotations

import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class ImageEnhancer:
    """Apply various image enhancement operations.

    Example::

        enhancer = ImageEnhancer()
        enhanced = enhancer.enhance(image, denoise=True, sharpen=True)
        bright   = enhancer.adjust_brightness(image, factor=1.5)
    """

    def enhance(
        self,
        image: np.ndarray,
        denoise: bool = True,
        sharpen: bool = False,
        clahe: bool = True,
        low_light: bool = False,
    ) -> np.ndarray:
        """Apply a pipeline of enhancement steps.

        Args:
            image: BGR numpy array.
            denoise: Apply bilateral denoising.
            sharpen: Apply unsharp masking.
            clahe: Apply CLAHE contrast enhancement.
            low_light: Apply gamma correction for dark images.

        Returns:
            Enhanced BGR image of the same shape.
        """
        out = image.copy()
        if denoise:
            out = self.denoise(out)
        if low_light:
            out = self.enhance_low_light(out)
        if clahe:
            out = self.apply_clahe(out)
        if sharpen:
            out = self.sharpen(out)
        return out

    def denoise(self, image: np.ndarray, strength: int = 10) -> np.ndarray:
        """Fast bilateral denoising.

        Args:
            image: BGR numpy array.
            strength: Filter diameter and sigma values.

        Returns:
            Denoised image.
        """
        try:
            import cv2
            return cv2.bilateralFilter(image, strength, strength * 2, strength // 2)
        except Exception as exc:
            logger.warning("ImageEnhancer.denoise failed: %s", exc)
            return image

    def sharpen(self, image: np.ndarray, amount: float = 1.5) -> np.ndarray:
        """Unsharp masking for edge sharpening.

        Args:
            image: BGR numpy array.
            amount: Sharpening strength multiplier.

        Returns:
            Sharpened image.
        """
        try:
            import cv2

            blur = cv2.GaussianBlur(image, (0, 0), sigmaX=3)
            return cv2.addWeighted(image, 1 + amount, blur, -amount, 0)
        except Exception as exc:
            logger.warning("ImageEnhancer.sharpen failed: %s", exc)
            return image

    def apply_clahe(
        self,
        image: np.ndarray,
        clip_limit: float = 2.0,
        tile_grid: Tuple[int, int] = (8, 8),
    ) -> np.ndarray:
        """Apply CLAHE contrast enhancement.

        Args:
            image: BGR numpy array.
            clip_limit: Contrast limiting threshold.
            tile_grid: Grid size for local histograms.

        Returns:
            Contrast-enhanced image.
        """
        try:
            import cv2

            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_ch, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
            l_eq = clahe.apply(l_ch)
            merged = cv2.merge([l_eq, a, b])
            return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        except Exception as exc:
            logger.warning("ImageEnhancer.apply_clahe failed: %s", exc)
            return image

    def enhance_low_light(
        self, image: np.ndarray, gamma: float = 2.2
    ) -> np.ndarray:
        """Gamma correction for low-light enhancement.

        Args:
            image: BGR numpy array.
            gamma: Gamma value > 1 brightens, < 1 darkens.

        Returns:
            Gamma-corrected image.
        """
        try:
            inv_gamma = 1.0 / gamma
            table = np.array(
                [(i / 255.0) ** inv_gamma * 255 for i in range(256)],
                dtype=np.uint8,
            )
            import cv2
            return cv2.LUT(image, table)
        except Exception as exc:
            logger.warning("ImageEnhancer.enhance_low_light failed: %s", exc)
            return image

    def adjust_brightness(
        self, image: np.ndarray, factor: float = 1.0
    ) -> np.ndarray:
        """Scale image brightness by *factor*.

        Args:
            image: BGR numpy array.
            factor: Multiplier > 1 brightens, < 1 darkens.

        Returns:
            Brightness-adjusted image.
        """
        return np.clip(image.astype(np.float32) * factor, 0, 255).astype(np.uint8)

    def adjust_contrast(
        self, image: np.ndarray, alpha: float = 1.0, beta: float = 0.0
    ) -> np.ndarray:
        """Adjust contrast and brightness with ``output = alpha * input + beta``.

        Args:
            image: BGR numpy array.
            alpha: Contrast multiplier.
            beta: Brightness offset.

        Returns:
            Adjusted image.
        """
        return np.clip(image.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
