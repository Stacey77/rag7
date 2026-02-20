"""Market simulator: Geometric Brownian Motion price path generation.

Provides :class:`MarketSimulator` for simulating realistic equity price paths
using continuous-time GBM with optional jump-diffusion.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class MarketSimulator:
    """Simulate asset price paths using Geometric Brownian Motion.

    Implements continuous GBM:
        ``S(t+dt) = S(t) * exp((mu - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z)``

    where *Z* ~ N(0, 1).

    Optionally adds Poisson jump-diffusion for fat-tail modelling.

    Attributes:
        seed: Optional random seed for reproducibility.
        use_jumps: Whether to add Poisson jump-diffusion.
        jump_intensity: Expected number of jumps per year (lambda).
        jump_mean: Mean log-jump size.
        jump_std: Standard deviation of log-jump size.
    """

    def __init__(
        self,
        seed: int | None = None,
        use_jumps: bool = False,
        jump_intensity: float = 2.0,
        jump_mean: float = -0.05,
        jump_std: float = 0.10,
    ) -> None:
        """Initialise MarketSimulator.

        Args:
            seed: NumPy random seed (None for non-deterministic).
            use_jumps: Enable jump-diffusion component.
            jump_intensity: Average jumps per year.
            jump_mean: Mean of log-normal jump size distribution.
            jump_std: Std-dev of log-normal jump size distribution.
        """
        self.seed = seed
        self.use_jumps = use_jumps
        self.jump_intensity = jump_intensity
        self.jump_mean = jump_mean
        self.jump_std = jump_std
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def simulate(
        self,
        s0: float = 100.0,
        mu: float = 0.05,
        sigma: float = 0.20,
        n_steps: int = 252,
        dt: float = 1 / 252,
    ) -> np.ndarray:
        """Simulate a single GBM price path.

        Args:
            s0: Initial asset price.
            mu: Annual expected return (drift).
            sigma: Annual volatility.
            n_steps: Number of time steps.
            dt: Length of each time step in years (default: 1 trading day).

        Returns:
            Price path array of length ``n_steps + 1`` (includes initial price).

        Raises:
            ValueError: If s0, sigma, or n_steps are non-positive.
        """
        if s0 <= 0:
            raise ValueError("s0 must be positive.")
        if sigma < 0:
            raise ValueError("sigma must be non-negative.")
        if n_steps <= 0:
            raise ValueError("n_steps must be positive.")

        prices = np.empty(n_steps + 1)
        prices[0] = s0

        z = self._rng.standard_normal(n_steps)
        drift_term = (mu - 0.5 * sigma ** 2) * dt
        diffusion_term = sigma * np.sqrt(dt) * z

        log_returns = drift_term + diffusion_term

        if self.use_jumps:
            # Poisson number of jumps per step
            n_jumps = self._rng.poisson(self.jump_intensity * dt, n_steps)
            for i, nj in enumerate(n_jumps):
                if nj > 0:
                    jump_sizes = self._rng.normal(self.jump_mean, self.jump_std, nj)
                    log_returns[i] += np.sum(jump_sizes)

        for i in range(n_steps):
            prices[i + 1] = prices[i] * np.exp(log_returns[i])

        return prices

    def simulate_correlated(
        self,
        n_assets: int,
        correlation_matrix: Any,
        s0_vector: Any | None = None,
        mu_vector: Any | None = None,
        sigma_vector: Any | None = None,
        n_steps: int = 252,
        dt: float = 1 / 252,
    ) -> np.ndarray:
        """Simulate multiple correlated GBM price paths.

        Uses Cholesky decomposition to impose cross-asset correlations.

        Args:
            n_assets: Number of assets.
            correlation_matrix: Array-like of shape ``(n_assets, n_assets)``.
            s0_vector: Initial prices; defaults to all 100.
            mu_vector: Annual drifts; defaults to all 0.05.
            sigma_vector: Annual vols; defaults to all 0.20.
            n_steps: Number of time steps.
            dt: Step size in years.

        Returns:
            Price array of shape ``(n_assets, n_steps + 1)``.

        Raises:
            ValueError: If correlation matrix is not positive semi-definite.
        """
        corr = np.asarray(correlation_matrix, dtype=np.float64)
        if corr.shape != (n_assets, n_assets):
            raise ValueError("correlation_matrix shape must be (n_assets, n_assets).")

        s0 = np.asarray(s0_vector or np.full(n_assets, 100.0), dtype=float)
        mu = np.asarray(mu_vector or np.full(n_assets, 0.05), dtype=float)
        sigma = np.asarray(sigma_vector or np.full(n_assets, 0.20), dtype=float)

        try:
            chol = np.linalg.cholesky(corr)
        except np.linalg.LinAlgError as exc:
            raise ValueError("correlation_matrix is not positive definite.") from exc

        prices = np.empty((n_assets, n_steps + 1))
        prices[:, 0] = s0

        z_indep = self._rng.standard_normal((n_assets, n_steps))
        z_corr = chol @ z_indep

        for i in range(n_steps):
            log_ret = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z_corr[:, i]
            prices[:, i + 1] = prices[:, i] * np.exp(log_ret)

        logger.debug(
            f"Simulated {n_assets} correlated paths over {n_steps} steps"
        )
        return prices
