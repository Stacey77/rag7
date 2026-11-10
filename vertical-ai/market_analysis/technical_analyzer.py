"""Technical analysis: chart patterns and price indicators.

Provides the :class:`TechnicalAnalyzer` which computes common technical
indicators from OHLCV data using pure NumPy arithmetic.
"""

from __future__ import annotations

import asyncio
from typing import Any

import numpy as np
from loguru import logger


class TechnicalAnalyzer:
    """Compute technical indicators and detect chart patterns from OHLCV data.

    All heavy computation is delegated to NumPy vectorised operations so the
    class remains dependency-light while staying numerically correct.

    Attributes:
        sma_periods: Periods for Simple Moving Average computation.
        ema_periods: Periods for Exponential Moving Average computation.
        rsi_period: Look-back period for RSI.
        bb_period: Look-back period for Bollinger Bands.
        bb_std: Number of standard deviations for Bollinger Band width.
        atr_period: Look-back period for ATR.
        macd_fast: Fast EMA period for MACD.
        macd_slow: Slow EMA period for MACD.
        macd_signal: Signal EMA period for MACD.
    """

    def __init__(
        self,
        sma_periods: list[int] | None = None,
        ema_periods: list[int] | None = None,
        rsi_period: int = 14,
        bb_period: int = 20,
        bb_std: float = 2.0,
        atr_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
    ) -> None:
        """Initialise TechnicalAnalyzer with indicator parameters.

        Args:
            sma_periods: List of SMA look-back periods. Defaults to [20, 50, 200].
            ema_periods: List of EMA look-back periods. Defaults to [12, 26].
            rsi_period: RSI look-back period.
            bb_period: Bollinger Band look-back period.
            bb_std: Bollinger Band standard-deviation multiplier.
            atr_period: ATR look-back period.
            macd_fast: MACD fast EMA period.
            macd_slow: MACD slow EMA period.
            macd_signal: MACD signal-line EMA period.
        """
        self.sma_periods = sma_periods or [20, 50, 200]
        self.ema_periods = ema_periods or [12, 26]
        self.rsi_period = rsi_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.atr_period = atr_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_array(data: Any) -> np.ndarray:
        """Convert input to a float64 NumPy array.

        Args:
            data: Any array-like structure.

        Returns:
            1-D float64 NumPy array.

        Raises:
            ValueError: If conversion produces an empty array.
        """
        arr = np.asarray(data, dtype=np.float64)
        if arr.ndim != 1 or arr.size == 0:
            raise ValueError("Expected a non-empty 1-D array-like input.")
        return arr

    def _ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Compute Exponential Moving Average.

        Args:
            prices: 1-D price array.
            period: Look-back period.

        Returns:
            EMA values array of the same length as *prices* (initial values
            are NaN until enough data is available).
        """
        k = 2.0 / (period + 1)
        ema = np.full(len(prices), np.nan)
        # seed with simple average of the first *period* values
        if len(prices) < period:
            return ema
        ema[period - 1] = np.mean(prices[:period])
        for i in range(period, len(prices)):
            ema[i] = prices[i] * k + ema[i - 1] * (1 - k)
        return ema

    def _sma(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Compute Simple Moving Average using a sliding window.

        Args:
            prices: 1-D price array.
            period: Look-back period.

        Returns:
            SMA array (NaN for indices < period − 1).
        """
        sma = np.full(len(prices), np.nan)
        if len(prices) < period:
            return sma
        cumsum = np.cumsum(prices)
        sma[period - 1:] = (
            cumsum[period - 1:]
            - np.concatenate(([0.0], cumsum[: len(prices) - period]))
        ) / period
        return sma

    def _rsi(self, prices: np.ndarray) -> np.ndarray:
        """Compute Relative Strength Index.

        Args:
            prices: 1-D close price array.

        Returns:
            RSI array in the range [0, 100].
        """
        period = self.rsi_period
        rsi = np.full(len(prices), np.nan)
        if len(prices) <= period:
            return rsi

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        for i in range(period, len(prices) - 1):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else np.inf
            rsi[i + 1] = 100.0 - (100.0 / (1.0 + rs))

        return rsi

    def _bollinger_bands(
        self, prices: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute Bollinger Bands (upper, middle, lower).

        Args:
            prices: 1-D close price array.

        Returns:
            Tuple of (upper_band, middle_band, lower_band) arrays.
        """
        middle = self._sma(prices, self.bb_period)
        std = np.full(len(prices), np.nan)
        for i in range(self.bb_period - 1, len(prices)):
            std[i] = np.std(prices[i - self.bb_period + 1: i + 1], ddof=0)
        upper = middle + self.bb_std * std
        lower = middle - self.bb_std * std
        return upper, middle, lower

    def _atr(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> np.ndarray:
        """Compute Average True Range.

        Args:
            high: High prices array.
            low: Low prices array.
            close: Close prices array.

        Returns:
            ATR array.
        """
        n = len(close)
        atr = np.full(n, np.nan)
        if n < 2:
            return atr

        tr = np.zeros(n)
        tr[0] = high[0] - low[0]
        for i in range(1, n):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )

        period = self.atr_period
        if n < period:
            return atr
        atr[period - 1] = np.mean(tr[:period])
        for i in range(period, n):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
        return atr

    def _macd(
        self, prices: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute MACD, signal line, and histogram.

        Args:
            prices: 1-D close price array.

        Returns:
            Tuple of (macd_line, signal_line, histogram) arrays.
        """
        fast_ema = self._ema(prices, self.macd_fast)
        slow_ema = self._ema(prices, self.macd_slow)
        macd_line = fast_ema - slow_ema
        # build signal only where macd_line is valid
        signal = self._ema(
            np.where(np.isnan(macd_line), 0.0, macd_line), self.macd_signal
        )
        histogram = macd_line - signal
        return macd_line, signal, histogram

    # ------------------------------------------------------------------
    # Public async interface
    # ------------------------------------------------------------------

    async def analyze(self, ohlcv_data: dict[str, Any]) -> dict[str, Any]:
        """Compute all technical indicators from OHLCV data.

        The computation is CPU-bound; the method uses
        ``asyncio.get_event_loop().run_in_executor`` to avoid blocking the
        event loop.

        Args:
            ohlcv_data: Dict with keys ``open``, ``high``, ``low``, ``close``,
                ``volume`` each mapped to an array-like of numeric values.

        Returns:
            Dict of indicator results.  Each value is a list (NaN → None) or
            a nested dict of lists.

        Raises:
            KeyError: If a required OHLCV key is missing.
            ValueError: If arrays are empty or mis-shaped.
        """
        required = {"open", "high", "low", "close", "volume"}
        missing = required - ohlcv_data.keys()
        if missing:
            raise KeyError(f"Missing OHLCV keys: {missing}")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._compute_indicators, ohlcv_data)

    def _compute_indicators(self, ohlcv_data: dict[str, Any]) -> dict[str, Any]:
        """Synchronous indicator computation (runs in a thread-pool executor).

        Args:
            ohlcv_data: Validated OHLCV dict.

        Returns:
            Indicator dict.
        """
        logger.debug("Computing technical indicators")
        close = self._to_array(ohlcv_data["close"])
        high = self._to_array(ohlcv_data["high"])
        low = self._to_array(ohlcv_data["low"])

        def to_list(arr: np.ndarray) -> list[float | None]:
            return [None if np.isnan(v) else float(v) for v in arr]

        sma_results = {
            f"sma_{p}": to_list(self._sma(close, p)) for p in self.sma_periods
        }
        ema_results = {
            f"ema_{p}": to_list(self._ema(close, p)) for p in self.ema_periods
        }

        upper_bb, mid_bb, lower_bb = self._bollinger_bands(close)
        macd_line, signal, histogram = self._macd(close)

        result: dict[str, Any] = {
            **sma_results,
            **ema_results,
            "rsi": to_list(self._rsi(close)),
            "bollinger_bands": {
                "upper": to_list(upper_bb),
                "middle": to_list(mid_bb),
                "lower": to_list(lower_bb),
            },
            "macd": {
                "macd": to_list(macd_line),
                "signal": to_list(signal),
                "histogram": to_list(histogram),
            },
            "atr": to_list(self._atr(high, low, close)),
        }

        logger.debug("Technical indicator computation complete")
        return result
