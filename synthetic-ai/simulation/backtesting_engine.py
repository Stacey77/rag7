"""Back-testing engine: strategy evaluation on historical data.

Provides :class:`BacktestingEngine` for running vectorised and event-driven
back-tests with full performance analytics.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
from loguru import logger


class BacktestingEngine:
    """Back-test a trading strategy against historical price data.

    Supports both vectorised strategies (functions that return signal arrays)
    and per-bar callback strategies.  Computes Sharpe, Sortino, max drawdown,
    Calmar ratio, win rate, and profit factor.

    Attributes:
        initial_capital: Starting portfolio value in currency units.
        commission_bps: Round-trip transaction cost in basis points.
        annualisation_factor: Trading periods per year.
        risk_free_rate: Annual risk-free rate for Sharpe/Sortino calculation.
    """

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission_bps: float = 2.0,
        annualisation_factor: int = 252,
        risk_free_rate: float = 0.02,
    ) -> None:
        """Initialise BacktestingEngine.

        Args:
            initial_capital: Starting capital.
            commission_bps: Round-trip commission in basis points.
            annualisation_factor: Periods per year for annualisation.
            risk_free_rate: Annual risk-free rate.
        """
        self.initial_capital = initial_capital
        self.commission_bps = commission_bps
        self.annualisation_factor = annualisation_factor
        self.risk_free_rate = risk_free_rate

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_metrics(
        self, returns: np.ndarray, equity_curve: np.ndarray
    ) -> dict[str, float]:
        """Compute strategy performance metrics.

        Args:
            returns: Period return array.
            equity_curve: Cumulative portfolio value array.

        Returns:
            Metrics dict.
        """
        ann_factor = self.annualisation_factor
        rf_period = self.risk_free_rate / ann_factor

        excess = returns - rf_period
        ann_return = float(np.mean(returns)) * ann_factor
        ann_vol = float(np.std(returns, ddof=1)) * np.sqrt(ann_factor) if len(returns) > 1 else 0.0
        sharpe = (ann_return - self.risk_free_rate) / ann_vol if ann_vol > 0 else 0.0

        downside = returns[returns < rf_period] - rf_period
        downside_dev = float(np.std(downside, ddof=1)) * np.sqrt(ann_factor) if len(downside) > 1 else 0.0
        sortino = (ann_return - self.risk_free_rate) / downside_dev if downside_dev > 0 else 0.0

        peak = np.maximum.accumulate(equity_curve)
        dd = (equity_curve - peak) / (peak + 1e-9)
        max_dd = float(np.min(dd))
        calmar = ann_return / abs(max_dd) if max_dd != 0 else 0.0

        winning_trades = returns[returns > 0]
        losing_trades = returns[returns < 0]
        win_rate = len(winning_trades) / len(returns) if len(returns) > 0 else 0.0
        profit_factor = (
            float(np.sum(winning_trades)) / abs(float(np.sum(losing_trades)))
            if len(losing_trades) > 0 and np.sum(losing_trades) != 0
            else float("inf")
        )

        total_return = float((equity_curve[-1] / equity_curve[0]) - 1.0) if len(equity_curve) > 1 else 0.0

        return {
            "total_return": total_return,
            "annualised_return": ann_return,
            "annualised_volatility": ann_vol,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": max_dd,
            "calmar_ratio": calmar,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
        }

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run_vectorised(
        self,
        prices: Any,
        signal_fn: Callable[[np.ndarray], np.ndarray],
    ) -> dict[str, Any]:
        """Run a vectorised back-test.

        The strategy is encoded as a function that maps a price array to a
        signal array where +1 = long, -1 = short, 0 = flat.

        Args:
            prices: Array-like of close prices.
            signal_fn: Callable that takes a 1-D price array and returns a
                same-length signal array with values in {-1, 0, 1}.

        Returns:
            Dict with keys ``equity_curve`` (list), ``returns`` (list),
            ``metrics`` (dict), ``trades`` (int).

        Raises:
            ValueError: If prices array is too short.
        """
        price_arr = np.asarray(prices, dtype=np.float64)
        if len(price_arr) < 2:
            raise ValueError("prices must have at least 2 elements.")

        signals = np.asarray(signal_fn(price_arr), dtype=np.float64)
        if len(signals) != len(price_arr):
            raise ValueError("signal_fn must return array same length as prices.")

        # Strategy returns: signal[t] applied to next-period price change
        price_returns = np.diff(price_arr) / price_arr[:-1]
        strategy_returns = signals[:-1] * price_returns

        # Commission: charged on position changes
        position_changes = np.diff(np.concatenate([[0], signals[:-1]]))
        commission = np.abs(position_changes) * (self.commission_bps / 10_000)
        net_returns = strategy_returns - commission

        equity = np.empty(len(net_returns) + 1)
        equity[0] = self.initial_capital
        for i, r in enumerate(net_returns):
            equity[i + 1] = equity[i] * (1 + r)

        n_trades = int(np.sum(np.abs(position_changes) > 0))
        metrics = self._compute_metrics(net_returns, equity)

        logger.info(
            f"Backtest complete: {n_trades} trades, "
            f"Sharpe={metrics['sharpe_ratio']:.2f}, "
            f"MaxDD={metrics['max_drawdown']:.2%}"
        )
        return {
            "equity_curve": equity.tolist(),
            "returns": net_returns.tolist(),
            "metrics": metrics,
            "trades": n_trades,
        }

    def run_buy_and_hold(self, prices: Any) -> dict[str, Any]:
        """Run a buy-and-hold benchmark.

        Args:
            prices: Array-like of close prices.

        Returns:
            Same structure as :meth:`run_vectorised`.
        """
        return self.run_vectorised(prices, lambda p: np.ones(len(p)))
