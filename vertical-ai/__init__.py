"""Vertical AI – domain-specific trading intelligence module.

This package exposes the :class:`VerticalAI` orchestrator which wires together
market analysis, risk management, order execution, and compliance sub-systems.
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from vertical_ai.market_analysis.technical_analyzer import TechnicalAnalyzer
from vertical_ai.market_analysis.fundamental_analyzer import FundamentalAnalyzer
from vertical_ai.market_analysis.sentiment_analyzer import SentimentAnalyzer
from vertical_ai.market_analysis.orderbook_analyzer import OrderBookAnalyzer
from vertical_ai.risk_management.portfolio_risk import PortfolioRisk
from vertical_ai.risk_management.position_sizer import PositionSizer
from vertical_ai.risk_management.correlation_analyzer import CorrelationAnalyzer
from vertical_ai.execution.smart_order_router import SmartOrderRouter
from vertical_ai.execution.slippage_predictor import SlippagePredictor
from vertical_ai.execution.market_impact_model import MarketImpactModel
from vertical_ai.compliance.regulatory_checker import RegulatoryChecker
from vertical_ai.compliance.audit_logger import AuditLogger


class VerticalAI:
    """Top-level orchestrator for the Vertical AI trading intelligence stack.

    Wires together all sub-systems and exposes a unified async interface for
    market analysis, risk evaluation, order routing, and compliance checks.

    Attributes:
        technical: Technical chart-pattern and indicator analyser.
        fundamental: Financial-ratio analyser.
        sentiment: News / social-media sentiment scorer.
        orderbook: Market-depth and liquidity analyser.
        portfolio_risk: VaR / CVaR / drawdown risk engine.
        position_sizer: Kelly / fixed-fraction / vol-targeting sizer.
        correlation: Rolling asset-correlation tracker.
        router: Smart order router.
        slippage: Slippage cost predictor.
        market_impact: Square-root market-impact model.
        compliance: Regulatory rule checker.
        audit: Structured audit logger.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialise VerticalAI and all sub-systems.

        Args:
            config: Optional configuration overrides keyed by sub-system name.
        """
        cfg = config or {}
        logger.info("Initialising VerticalAI")

        self.technical = TechnicalAnalyzer(**cfg.get("technical", {}))
        self.fundamental = FundamentalAnalyzer(**cfg.get("fundamental", {}))
        self.sentiment = SentimentAnalyzer(**cfg.get("sentiment", {}))
        self.orderbook = OrderBookAnalyzer(**cfg.get("orderbook", {}))

        self.portfolio_risk = PortfolioRisk(**cfg.get("portfolio_risk", {}))
        self.position_sizer = PositionSizer(**cfg.get("position_sizer", {}))
        self.correlation = CorrelationAnalyzer(**cfg.get("correlation", {}))

        self.router = SmartOrderRouter(**cfg.get("router", {}))
        self.slippage = SlippagePredictor(**cfg.get("slippage", {}))
        self.market_impact = MarketImpactModel(**cfg.get("market_impact", {}))

        self.compliance = RegulatoryChecker(**cfg.get("compliance", {}))
        self.audit = AuditLogger(**cfg.get("audit", {}))

        logger.info("VerticalAI initialised successfully")

    async def full_analysis(
        self,
        ohlcv_data: dict[str, Any],
        orderbook: dict[str, Any],
        financial_data: dict[str, Any],
        texts: list[str],
    ) -> dict[str, Any]:
        """Run all market-analysis components concurrently.

        Args:
            ohlcv_data: OHLCV price data dict with keys ``open``, ``high``,
                ``low``, ``close``, ``volume`` as array-like sequences.
            orderbook: Order-book snapshot with ``bids`` and ``asks`` lists of
                ``[price, size]`` pairs.
            financial_data: Company financial metrics dict.
            texts: List of news / social-media text strings to score.

        Returns:
            Aggregated analysis results keyed by sub-system name.

        Raises:
            ValueError: If any required data field is missing.
        """
        logger.info("Starting full market analysis")
        technical_task = self.technical.analyze(ohlcv_data)
        orderbook_task = self.orderbook.analyze(orderbook)
        results = await asyncio.gather(technical_task, orderbook_task)

        fundamental_result = self.fundamental.analyze_fundamentals(financial_data)
        sentiment_result = self.sentiment.analyze_sentiment(texts)

        return {
            "technical": results[0],
            "orderbook": results[1],
            "fundamental": fundamental_result,
            "sentiment": sentiment_result,
        }


__all__ = ["VerticalAI"]
