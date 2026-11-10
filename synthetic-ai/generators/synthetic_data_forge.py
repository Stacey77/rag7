"""Synthetic data forge: training data augmentation for financial time series.

Provides :class:`SyntheticDataForge` which augments price series using noise
injection, time warping, window slicing, and magnitude scaling techniques.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class SyntheticDataForge:
    """Augment financial time series to create additional training samples.

    Implements four augmentation primitives:

    * **Noise injection** – add Gaussian noise scaled to series volatility.
    * **Time warping** – non-uniform time axis compression / expansion.
    * **Window slicing** – extract random sub-windows and rescale.
    * **Magnitude scaling** – globally scale the series by a random factor.

    Attributes:
        seed: Random seed for reproducibility.
        noise_scale: Fraction of series std-dev used for noise injection.
        warp_knots: Number of interpolation knots for time warping.
        scale_range: ``(min_factor, max_factor)`` for magnitude scaling.
    """

    def __init__(
        self,
        seed: int | None = None,
        noise_scale: float = 0.05,
        warp_knots: int = 4,
        scale_range: tuple[float, float] = (0.8, 1.2),
    ) -> None:
        """Initialise SyntheticDataForge.

        Args:
            seed: NumPy random seed.
            noise_scale: Noise amplitude as a multiple of the series std-dev.
            warp_knots: Number of internal knot points for time warping.
            scale_range: Min and max scaling factors for magnitude scaling.
        """
        self.noise_scale = noise_scale
        self.warp_knots = warp_knots
        self.scale_range = scale_range
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Augmentation primitives
    # ------------------------------------------------------------------

    def inject_noise(self, series: Any) -> np.ndarray:
        """Add Gaussian noise to a price series.

        Args:
            series: 1-D array-like of price values.

        Returns:
            Augmented series with noise added.
        """
        arr = np.asarray(series, dtype=np.float64)
        std = float(np.std(arr)) if len(arr) > 1 else 1.0
        noise = self._rng.normal(0, self.noise_scale * std, size=arr.shape)
        return arr + noise

    def time_warp(self, series: Any) -> np.ndarray:
        """Apply non-uniform time axis compression / expansion.

        Generates a smooth random warp function using piecewise linear
        interpolation, then resamples the original series.

        Args:
            series: 1-D array-like price series.

        Returns:
            Time-warped series of the same length.
        """
        arr = np.asarray(series, dtype=np.float64)
        n = len(arr)
        if n < 4:
            return arr.copy()

        # Random warp magnitudes at knot points
        knot_x = np.linspace(0, n - 1, self.warp_knots + 2)
        knot_y = knot_x + self._rng.uniform(-n * 0.1, n * 0.1, size=len(knot_x))
        knot_y[0] = 0.0
        knot_y[-1] = n - 1
        knot_y = np.clip(knot_y, 0, n - 1)
        knot_y = np.sort(knot_y)

        # Interpolate warp function at all integer indices
        warp_indices = np.interp(np.arange(n), knot_x, knot_y)
        return np.interp(warp_indices, np.arange(n), arr)

    def window_slice(self, series: Any, window_fraction: float = 0.9) -> np.ndarray:
        """Extract a random sub-window and rescale back to original length.

        Args:
            series: 1-D array-like price series.
            window_fraction: Fraction of series to include in the slice
                (0 < f < 1).

        Returns:
            Sliced and resampled series of the original length.

        Raises:
            ValueError: If window_fraction is outside (0, 1).
        """
        if not 0 < window_fraction < 1:
            raise ValueError("window_fraction must be in (0, 1).")
        arr = np.asarray(series, dtype=np.float64)
        n = len(arr)
        window_size = max(2, int(n * window_fraction))
        start = int(self._rng.integers(0, n - window_size + 1))
        sliced = arr[start: start + window_size]
        return np.interp(np.linspace(0, len(sliced) - 1, n), np.arange(len(sliced)), sliced)

    def magnitude_scale(self, series: Any) -> np.ndarray:
        """Globally scale a series by a random factor.

        Args:
            series: 1-D array-like price series.

        Returns:
            Scaled series.
        """
        arr = np.asarray(series, dtype=np.float64)
        factor = self._rng.uniform(*self.scale_range)
        return arr * factor

    # ------------------------------------------------------------------
    # High-level augmentation
    # ------------------------------------------------------------------

    def augment(
        self,
        series: Any,
        n_samples: int = 10,
        methods: list[str] | None = None,
    ) -> list[np.ndarray]:
        """Generate multiple augmented versions of a series.

        Args:
            series: Base price series.
            n_samples: Number of augmented samples to generate.
            methods: List of method names to apply (in order) per sample.
                Defaults to all four methods.

        Returns:
            List of *n_samples* augmented NumPy arrays.

        Raises:
            ValueError: If an unknown method name is provided.
        """
        available = {
            "noise": self.inject_noise,
            "warp": self.time_warp,
            "slice": self.window_slice,
            "scale": self.magnitude_scale,
        }
        chosen = methods or list(available.keys())
        for m in chosen:
            if m not in available:
                raise ValueError(f"Unknown augmentation method '{m}'. Options: {list(available)}")

        arr = np.asarray(series, dtype=np.float64)
        samples: list[np.ndarray] = []
        for _ in range(n_samples):
            augmented = arr.copy()
            # Randomly apply a random subset of the chosen methods
            k = int(self._rng.integers(1, len(chosen) + 1))
            selected = self._rng.choice(chosen, size=k, replace=False)
            for method_name in selected:
                augmented = available[method_name](augmented)
            samples.append(augmented)

        logger.debug(f"Augmented {n_samples} samples using methods: {chosen}")
        return samples
