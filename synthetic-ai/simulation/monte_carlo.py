"""Monte Carlo simulation: probabilistic scenario modelling.

Provides :class:`MonteCarlo` for multi-path price simulation, portfolio
terminal-value distributions, and Value-at-Risk estimation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats
from loguru import logger


class MonteCarlo:
    """Run Monte Carlo simulations for probabilistic financial modelling.

    Supports multiple return distributions (normal, t-distribution, uniform)
    and provides percentile-based risk metrics over the simulated ensemble.

    Attributes:
        n_simulations: Number of simulation paths.
        seed: Random seed.
        distribution: Return distribution (``"normal"``, ``"t"``, or
            ``"uniform"``).
        t_df: Degrees of freedom for the Student-t distribution.
    """

    def __init__(
        self,
        n_simulations: int = 10_000,
        seed: int | None = None,
        distribution: str = "normal",
        t_df: float = 5.0,
    ) -> None:
        """Initialise MonteCarlo.

        Args:
            n_simulations: Number of Monte Carlo paths.
            seed: Random seed for reproducibility.
            distribution: Sampling distribution for returns.
            t_df: Degrees of freedom for Student-t (only used when
                distribution = ``"t"``).

        Raises:
            ValueError: If distribution is not supported.
        """
        supported = ("normal", "t", "uniform")
        if distribution not in supported:
            raise ValueError(f"distribution must be one of {supported}.")
        self.n_simulations = n_simulations
        self.seed = seed
        self.distribution = distribution
        self.t_df = t_df
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sample_returns(self, mu: float, sigma: float, n_steps: int) -> np.ndarray:
        """Sample a return matrix from the configured distribution.

        Args:
            mu: Per-step mean return.
            sigma: Per-step standard deviation.
            n_steps: Number of steps per path.

        Returns:
            Return matrix of shape ``(n_simulations, n_steps)``.
        """
        shape = (self.n_simulations, n_steps)
        if self.distribution == "normal":
            return self._rng.normal(mu, sigma, shape)
        if self.distribution == "t":
            raw = self._rng.standard_t(self.t_df, shape)
            raw_std = np.sqrt(self.t_df / (self.t_df - 2)) if self.t_df > 2 else 1.0
            return mu + sigma * raw / raw_std
        # uniform
        half = sigma * np.sqrt(3)
        return self._rng.uniform(mu - half, mu + half, shape)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def simulate_paths(
        self,
        s0: float,
        mu: float,
        sigma: float,
        n_steps: int,
        dt: float = 1 / 252,
    ) -> np.ndarray:
        """Simulate price paths using log-normal evolution.

        Args:
            s0: Initial price.
            mu: Annual drift.
            sigma: Annual volatility.
            n_steps: Number of time steps.
            dt: Step size in years.

        Returns:
            Price matrix of shape ``(n_simulations, n_steps + 1)``.
        """
        step_mu = (mu - 0.5 * sigma ** 2) * dt
        step_sigma = sigma * np.sqrt(dt)
        log_returns = self._sample_returns(step_mu, step_sigma, n_steps)
        log_prices = np.concatenate(
            [np.full((self.n_simulations, 1), np.log(s0)), np.cumsum(log_returns, axis=1)],
            axis=1,
        )
        return np.exp(log_prices)

    def terminal_distribution(
        self,
        s0: float,
        mu: float,
        sigma: float,
        n_steps: int,
        dt: float = 1 / 252,
    ) -> dict[str, Any]:
        """Compute statistics of the terminal price distribution.

        Args:
            s0: Initial price.
            mu: Annual drift.
            sigma: Annual volatility.
            n_steps: Number of steps to horizon.
            dt: Step size in years.

        Returns:
            Dict with percentile prices, mean, std, skewness, kurtosis,
            VaR at 95%, and probability of loss.
        """
        paths = self.simulate_paths(s0, mu, sigma, n_steps, dt)
        terminals = paths[:, -1]

        returns = (terminals - s0) / s0
        var_95 = float(np.percentile(returns, 5))

        logger.debug(
            f"Monte Carlo terminal distribution: mean={float(np.mean(terminals)):.2f}, "
            f"std={float(np.std(terminals)):.2f}"
        )
        return {
            "mean_price": float(np.mean(terminals)),
            "std_price": float(np.std(terminals)),
            "median_price": float(np.median(terminals)),
            "p5_price": float(np.percentile(terminals, 5)),
            "p25_price": float(np.percentile(terminals, 25)),
            "p75_price": float(np.percentile(terminals, 75)),
            "p95_price": float(np.percentile(terminals, 95)),
            "skewness": float(stats.skew(terminals)),
            "kurtosis": float(stats.kurtosis(terminals)),
            "var_95_return": var_95,
            "prob_loss": float(np.mean(terminals < s0)),
            "n_simulations": self.n_simulations,
        }

    def estimate_var(
        self,
        portfolio_value: float,
        mu: float,
        sigma: float,
        horizon_days: int = 1,
        confidence_level: float = 0.95,
    ) -> dict[str, float]:
        """Estimate portfolio Value-at-Risk via Monte Carlo.

        Args:
            portfolio_value: Current portfolio value.
            mu: Daily expected return.
            sigma: Daily volatility.
            horizon_days: Risk horizon in days.
            confidence_level: Confidence level (e.g., 0.95).

        Returns:
            Dict with ``var_amount``, ``var_pct``, ``cvar_amount``, ``cvar_pct``.
        """
        paths = self.simulate_paths(portfolio_value, mu, sigma, horizon_days, dt=1.0)
        terminals = paths[:, -1]
        returns = (terminals - portfolio_value) / portfolio_value

        cutoff_pct = (1 - confidence_level) * 100
        var_pct = float(-np.percentile(returns, cutoff_pct))
        tail_returns = returns[returns <= -var_pct]
        cvar_pct = float(-np.mean(tail_returns)) if len(tail_returns) > 0 else var_pct

        return {
            "var_amount": round(portfolio_value * var_pct, 2),
            "var_pct": round(var_pct, 6),
            "cvar_amount": round(portfolio_value * cvar_pct, 2),
            "cvar_pct": round(cvar_pct, 6),
        }
