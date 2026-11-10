"""Fundamental analysis: financial ratio computation and scoring.

Provides the :class:`FundamentalAnalyzer` for evaluating company financials
through common valuation and health ratios.
"""

from __future__ import annotations

from typing import Any

from loguru import logger


class FundamentalAnalyzer:
    """Analyse company financial data through standard valuation ratios.

    Computes valuation (P/E, P/B, EV/EBITDA), profitability (ROE, ROA, profit
    margin), and leverage (debt-to-equity, current ratio, interest coverage)
    metrics from raw financial statement data.

    Attributes:
        thresholds: Dict of ratio name → (low_threshold, high_threshold)
            used to tag ratios as ``"undervalued"``, ``"fair"``, or
            ``"overvalued"``/``"risky"``.
    """

    _DEFAULT_THRESHOLDS: dict[str, tuple[float, float]] = {
        "pe_ratio": (0.0, 25.0),
        "pb_ratio": (0.0, 3.0),
        "ev_ebitda": (0.0, 15.0),
        "roe": (0.10, 0.30),
        "roa": (0.05, 0.20),
        "profit_margin": (0.05, 0.30),
        "debt_to_equity": (0.0, 1.0),
        "current_ratio": (1.5, 3.0),
        "interest_coverage": (3.0, 10.0),
    }

    def __init__(
        self,
        thresholds: dict[str, tuple[float, float]] | None = None,
    ) -> None:
        """Initialise FundamentalAnalyzer.

        Args:
            thresholds: Override default ratio threshold bands.  Each entry
                maps a ratio name to ``(min_good, max_good)`` bounds.
        """
        self.thresholds: dict[str, tuple[float, float]] = {
            **self._DEFAULT_THRESHOLDS,
            **(thresholds or {}),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_div(numerator: float, denominator: float, default: float = float("nan")) -> float:
        """Return numerator / denominator, or *default* on zero-division.

        Args:
            numerator: Dividend value.
            denominator: Divisor value.
            default: Fallback when denominator is zero.

        Returns:
            Computed ratio or *default*.
        """
        if denominator == 0:
            return default
        return numerator / denominator

    def _score_ratio(self, name: str, value: float) -> str:
        """Classify a ratio as ``healthy``, ``low``, or ``high``.

        Args:
            name: Ratio name (must exist in :attr:`thresholds`).
            value: Computed ratio value.

        Returns:
            Classification string.
        """
        if name not in self.thresholds:
            return "unknown"
        low, high = self.thresholds[name]
        if value < low:
            return "low"
        if value > high:
            return "high"
        return "healthy"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyze_fundamentals(self, financial_data: dict[str, Any]) -> dict[str, Any]:
        """Compute financial ratios from raw statement data.

        Args:
            financial_data: Dict containing any subset of the following keys:

                * ``price`` – current stock price
                * ``eps`` – earnings per share
                * ``book_value_per_share`` – book value per share
                * ``net_income`` – net income
                * ``revenue`` – total revenue
                * ``total_equity`` – shareholders' equity
                * ``total_assets`` – total assets
                * ``total_debt`` – total debt
                * ``current_assets`` – current assets
                * ``current_liabilities`` – current liabilities
                * ``ebit`` – EBIT
                * ``interest_expense`` – interest expense
                * ``enterprise_value`` – enterprise value
                * ``ebitda`` – EBITDA

        Returns:
            Dict with keys ``ratios`` (computed float values) and ``scores``
            (classification strings for each ratio).

        Raises:
            TypeError: If *financial_data* is not a dict.
        """
        if not isinstance(financial_data, dict):
            raise TypeError(f"financial_data must be a dict, got {type(financial_data)}")

        logger.debug("Computing fundamental ratios")
        fd = financial_data

        ratios: dict[str, float] = {}

        # Valuation
        ratios["pe_ratio"] = self._safe_div(
            fd.get("price", 0.0), fd.get("eps", 0.0)
        )
        ratios["pb_ratio"] = self._safe_div(
            fd.get("price", 0.0), fd.get("book_value_per_share", 0.0)
        )
        ratios["ev_ebitda"] = self._safe_div(
            fd.get("enterprise_value", 0.0), fd.get("ebitda", 0.0)
        )

        # Profitability
        ratios["roe"] = self._safe_div(
            fd.get("net_income", 0.0), fd.get("total_equity", 0.0)
        )
        ratios["roa"] = self._safe_div(
            fd.get("net_income", 0.0), fd.get("total_assets", 0.0)
        )
        ratios["profit_margin"] = self._safe_div(
            fd.get("net_income", 0.0), fd.get("revenue", 0.0)
        )

        # Leverage / liquidity
        ratios["debt_to_equity"] = self._safe_div(
            fd.get("total_debt", 0.0), fd.get("total_equity", 0.0)
        )
        ratios["current_ratio"] = self._safe_div(
            fd.get("current_assets", 0.0), fd.get("current_liabilities", 0.0)
        )
        ratios["interest_coverage"] = self._safe_div(
            fd.get("ebit", 0.0), fd.get("interest_expense", 0.0)
        )

        scores = {name: self._score_ratio(name, val) for name, val in ratios.items()}

        logger.debug(f"Fundamental analysis complete: {len(ratios)} ratios computed")
        return {"ratios": ratios, "scores": scores}
