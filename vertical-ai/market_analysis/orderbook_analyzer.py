"""Order-book analysis: market depth, bid-ask imbalance, and liquidity scoring.

Provides :class:`OrderBookAnalyzer` for real-time microstructure metrics.
"""

from __future__ import annotations

import asyncio
from typing import Any

import numpy as np
from loguru import logger


class OrderBookAnalyzer:
    """Analyse Level-2 order-book snapshots for microstructure metrics.

    Computes bid-ask spread, depth imbalance, weighted mid-price, and a
    composite liquidity score from raw order-book data.

    Attributes:
        depth_levels: Number of price levels to consider when computing
            liquidity and imbalance metrics.
        imbalance_alpha: Exponential smoothing factor for rolling imbalance.
    """

    def __init__(
        self,
        depth_levels: int = 10,
        imbalance_alpha: float = 0.1,
    ) -> None:
        """Initialise OrderBookAnalyzer.

        Args:
            depth_levels: How many top price levels to include in analysis.
            imbalance_alpha: EMA smoothing factor for running imbalance
                estimate (0 < alpha ≤ 1).
        """
        if not 0 < imbalance_alpha <= 1:
            raise ValueError("imbalance_alpha must be in (0, 1].")
        self.depth_levels = depth_levels
        self.imbalance_alpha = imbalance_alpha
        self._running_imbalance: float | None = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_side(
        side: list[list[float]], name: str
    ) -> tuple[np.ndarray, np.ndarray]:
        """Parse and validate one side of the order book.

        Args:
            side: List of ``[price, size]`` pairs.
            name: ``"bids"`` or ``"asks"`` (for error messages).

        Returns:
            Tuple of (prices, sizes) as float64 arrays.

        Raises:
            ValueError: If the side is empty or malformed.
        """
        if not side:
            raise ValueError(f"Order book '{name}' must not be empty.")
        arr = np.asarray(side, dtype=np.float64)
        if arr.ndim != 2 or arr.shape[1] < 2:
            raise ValueError(f"Each '{name}' entry must be [price, size].")
        return arr[:, 0], arr[:, 1]

    def _best_bid_ask(
        self,
        bid_prices: np.ndarray,
        ask_prices: np.ndarray,
    ) -> tuple[float, float]:
        """Return best bid and best ask prices.

        Args:
            bid_prices: All bid price levels.
            ask_prices: All ask price levels.

        Returns:
            Tuple of (best_bid, best_ask).
        """
        return float(np.max(bid_prices)), float(np.min(ask_prices))

    def _weighted_mid_price(
        self,
        best_bid: float,
        best_ask: float,
        bid_size_at_best: float,
        ask_size_at_best: float,
    ) -> float:
        """Compute size-weighted mid-price.

        Args:
            best_bid: Best bid price.
            best_ask: Best ask price.
            bid_size_at_best: Size at best bid.
            ask_size_at_best: Size at best ask.

        Returns:
            Weighted mid-price.
        """
        total = bid_size_at_best + ask_size_at_best
        if total == 0:
            return (best_bid + best_ask) / 2.0
        return (best_bid * ask_size_at_best + best_ask * bid_size_at_best) / total

    def _liquidity_score(
        self,
        bid_prices: np.ndarray,
        bid_sizes: np.ndarray,
        ask_prices: np.ndarray,
        ask_sizes: np.ndarray,
        spread: float,
        mid: float,
    ) -> float:
        """Compute a composite liquidity score in [0, 1].

        Combines spread tightness, total depth, and level count into a single
        normalised metric.

        Args:
            bid_prices: Bid price levels.
            bid_sizes: Bid size levels.
            ask_prices: Ask price levels.
            ask_sizes: Ask size levels.
            spread: Absolute bid-ask spread.
            mid: Mid-price.

        Returns:
            Liquidity score (higher is more liquid).
        """
        n = self.depth_levels
        bid_depth = np.sum(bid_sizes[:n]) if len(bid_sizes) >= n else np.sum(bid_sizes)
        ask_depth = np.sum(ask_sizes[:n]) if len(ask_sizes) >= n else np.sum(ask_sizes)
        total_depth = bid_depth + ask_depth

        spread_score = 1.0 / (1.0 + spread / (mid + 1e-9) * 100)
        depth_score = np.tanh(total_depth / 1000.0)

        return float(np.clip(0.5 * spread_score + 0.5 * depth_score, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Public async interface
    # ------------------------------------------------------------------

    async def analyze(self, orderbook: dict[str, Any]) -> dict[str, Any]:
        """Analyse an order-book snapshot asynchronously.

        Args:
            orderbook: Dict with keys:

                * ``bids`` – list of ``[price, size]`` pairs sorted
                  descending by price.
                * ``asks`` – list of ``[price, size]`` pairs sorted
                  ascending by price.

        Returns:
            Dict with keys ``best_bid``, ``best_ask``, ``spread``,
            ``spread_bps``, ``mid_price``, ``weighted_mid_price``,
            ``bid_ask_imbalance``, ``total_bid_depth``, ``total_ask_depth``,
            ``liquidity_score``.

        Raises:
            KeyError: If ``bids`` or ``asks`` keys are absent.
            ValueError: If order-book data is malformed.
        """
        for key in ("bids", "asks"):
            if key not in orderbook:
                raise KeyError(f"Order book missing required key: '{key}'")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._compute_metrics, orderbook)

    def _compute_metrics(self, orderbook: dict[str, Any]) -> dict[str, Any]:
        """Synchronous metric computation.

        Args:
            orderbook: Validated order-book dict.

        Returns:
            Metrics dict.
        """
        logger.debug("Computing order-book metrics")
        bid_prices, bid_sizes = self._validate_side(orderbook["bids"], "bids")
        ask_prices, ask_sizes = self._validate_side(orderbook["asks"], "asks")

        best_bid, best_ask = self._best_bid_ask(bid_prices, ask_prices)
        spread = best_ask - best_bid
        mid = (best_bid + best_ask) / 2.0
        spread_bps = (spread / mid) * 10_000 if mid > 0 else 0.0

        bid_best_idx = int(np.argmax(bid_prices))
        ask_best_idx = int(np.argmin(ask_prices))
        wmid = self._weighted_mid_price(
            best_bid, best_ask,
            float(bid_sizes[bid_best_idx]),
            float(ask_sizes[ask_best_idx]),
        )

        n = self.depth_levels
        total_bid = float(np.sum(bid_sizes[:n]))
        total_ask = float(np.sum(ask_sizes[:n]))
        imbalance = (total_bid - total_ask) / (total_bid + total_ask + 1e-9)

        # Update exponential running imbalance
        if self._running_imbalance is None:
            self._running_imbalance = imbalance
        else:
            self._running_imbalance = (
                self.imbalance_alpha * imbalance
                + (1 - self.imbalance_alpha) * self._running_imbalance
            )

        liq = self._liquidity_score(
            bid_prices, bid_sizes, ask_prices, ask_sizes, spread, mid
        )

        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "spread_bps": round(spread_bps, 4),
            "mid_price": mid,
            "weighted_mid_price": wmid,
            "bid_ask_imbalance": round(imbalance, 6),
            "running_imbalance": round(self._running_imbalance, 6),
            "total_bid_depth": total_bid,
            "total_ask_depth": total_ask,
            "liquidity_score": round(liq, 4),
        }
