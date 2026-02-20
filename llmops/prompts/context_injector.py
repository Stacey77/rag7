"""Dynamic context injection into prompts with market data and portfolio state."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from loguru import logger


@dataclass
class MarketContext:
    """Real-time market data context for prompt injection.

    Attributes:
        symbol: Trading instrument identifier.
        price: Current mid-price.
        bid: Current best bid.
        ask: Current best ask.
        volume_24h: 24-hour traded volume.
        price_change_pct: 24-hour price change percentage.
        high_24h: 24-hour high price.
        low_24h: 24-hour low price.
        timestamp: UTC time of the data snapshot.
    """

    symbol: str
    price: float
    bid: float
    ask: float
    volume_24h: float
    price_change_pct: float
    high_24h: float
    low_24h: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_text(self) -> str:
        """Render to a compact, human-readable block for prompt injection.

        Returns:
            Multi-line market data string.
        """
        return (
            f"Symbol: {self.symbol}\n"
            f"Price: {self.price:.4f} (Bid: {self.bid:.4f} / Ask: {self.ask:.4f})\n"
            f"24h Change: {self.price_change_pct:+.2f}%\n"
            f"24h Range: {self.low_24h:.4f} – {self.high_24h:.4f}\n"
            f"Volume (24h): {self.volume_24h:,.0f}\n"
            f"As of: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )


@dataclass
class PortfolioState:
    """Current portfolio state for prompt injection.

    Attributes:
        total_value: Total portfolio value in base currency.
        cash: Uninvested cash balance.
        positions: Mapping of symbol to position dict with keys
            ``"qty"``, ``"avg_cost"``, ``"pnl"``.
        unrealised_pnl: Total unrealised profit/loss.
        realised_pnl_today: Realised P&L for the current trading day.
        exposure_pct: Percentage of portfolio invested.
    """

    total_value: float
    cash: float
    positions: dict[str, dict[str, float]] = field(default_factory=dict)
    unrealised_pnl: float = 0.0
    realised_pnl_today: float = 0.0
    exposure_pct: float = 0.0

    def to_text(self) -> str:
        """Render to a compact, human-readable block.

        Returns:
            Multi-line portfolio summary string.
        """
        pos_lines = "\n".join(
            f"  {sym}: qty={p.get('qty', 0):.2f}, "
            f"avg_cost={p.get('avg_cost', 0):.4f}, "
            f"pnl={p.get('pnl', 0):+.2f}"
            for sym, p in self.positions.items()
        ) or "  (no open positions)"
        return (
            f"Total Value: {self.total_value:,.2f}\n"
            f"Cash: {self.cash:,.2f}\n"
            f"Exposure: {self.exposure_pct:.1f}%\n"
            f"Unrealised PnL: {self.unrealised_pnl:+,.2f}\n"
            f"Realised PnL (today): {self.realised_pnl_today:+,.2f}\n"
            f"Positions:\n{pos_lines}"
        )


@dataclass
class NewsContext:
    """Recent news headlines for prompt injection.

    Attributes:
        headlines: List of recent news headline strings.
        sentiment_score: Aggregate sentiment score (−1 to +1).
        source: News data source identifier.
        retrieved_at: UTC time of retrieval.
    """

    headlines: list[str]
    sentiment_score: float = 0.0
    source: str = "aggregated"
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_text(self, max_headlines: int = 5) -> str:
        """Render headlines to a compact block.

        Args:
            max_headlines: Maximum number of headlines to include.

        Returns:
            Multi-line news summary string.
        """
        top = self.headlines[:max_headlines]
        bullets = "\n".join(f"  • {h}" for h in top)
        return (
            f"Source: {self.source} | "
            f"Sentiment: {self.sentiment_score:+.2f}\n"
            f"{bullets}"
        )


class ContextInjector:
    """Dynamic context injection for trading platform prompts.

    Retrieves and formats market data, portfolio state, and news context
    for injection into LLM prompts at inference time.

    Attributes:
        _market_data_fetcher: Optional async callable returning
            :class:`MarketContext` for a given symbol.
        _portfolio_fetcher: Optional async callable returning
            :class:`PortfolioState`.
        _news_fetcher: Optional async callable returning
            :class:`NewsContext` for a given symbol.
        _cache: Simple in-memory context cache.
    """

    def __init__(
        self,
        market_data_fetcher: Any | None = None,
        portfolio_fetcher: Any | None = None,
        news_fetcher: Any | None = None,
    ) -> None:
        """Initialise the context injector.

        Args:
            market_data_fetcher: Optional async callable ``(symbol) → MarketContext``.
            portfolio_fetcher: Optional async callable ``() → PortfolioState``.
            news_fetcher: Optional async callable ``(symbol) → NewsContext``.
        """
        self._market_data_fetcher = market_data_fetcher
        self._portfolio_fetcher = portfolio_fetcher
        self._news_fetcher = news_fetcher
        self._cache: dict[str, Any] = {}
        logger.info("ContextInjector initialised")

    async def build_context(
        self,
        symbol: str,
        include_market: bool = True,
        include_portfolio: bool = True,
        include_news: bool = True,
    ) -> dict[str, str]:
        """Assemble all requested context blocks asynchronously.

        Args:
            symbol: Trading instrument symbol for market and news context.
            include_market: Whether to include market data context.
            include_portfolio: Whether to include portfolio state context.
            include_news: Whether to include news context.

        Returns:
            Mapping of context key (``"market"``, ``"portfolio"``, ``"news"``)
            to formatted text block.
        """
        tasks: dict[str, asyncio.Task[Any]] = {}

        if include_market:
            tasks["market"] = asyncio.create_task(self._get_market(symbol))
        if include_portfolio:
            tasks["portfolio"] = asyncio.create_task(self._get_portfolio())
        if include_news:
            tasks["news"] = asyncio.create_task(self._get_news(symbol))

        results: dict[str, str] = {}
        for key, task in tasks.items():
            try:
                value = await task
                results[key] = value
            except Exception as exc:
                logger.warning("Failed to fetch '{}' context: {}", key, exc)
                results[key] = f"(context unavailable: {exc})"

        return results

    def inject(self, prompt: str, context: dict[str, str]) -> str:
        """Prepend context blocks to a prompt string.

        Args:
            prompt: Base prompt text.
            context: Context mapping returned by :meth:`build_context`.

        Returns:
            Prompt with context prepended in a structured header.
        """
        if not context:
            return prompt

        header_parts: list[str] = ["=== LIVE CONTEXT ==="]
        for key, text in context.items():
            header_parts.append(f"[{key.upper()}]\n{text}")
        header_parts.append("=== END CONTEXT ===\n")
        header = "\n\n".join(header_parts)
        return f"{header}\n{prompt}"

    async def _get_market(self, symbol: str) -> str:
        """Fetch and format market data.

        Args:
            symbol: Instrument identifier.

        Returns:
            Formatted market data string.
        """
        if self._market_data_fetcher is not None:
            market: MarketContext = await self._market_data_fetcher(symbol)
            return market.to_text()
        # Simulated fallback
        await asyncio.sleep(0)
        return (
            f"Symbol: {symbol}\nPrice: N/A\n(live feed not configured)"
        )

    async def _get_portfolio(self) -> str:
        """Fetch and format portfolio state.

        Returns:
            Formatted portfolio summary string.
        """
        if self._portfolio_fetcher is not None:
            portfolio: PortfolioState = await self._portfolio_fetcher()
            return portfolio.to_text()
        await asyncio.sleep(0)
        return "Portfolio: N/A (feed not configured)"

    async def _get_news(self, symbol: str) -> str:
        """Fetch and format news context.

        Args:
            symbol: Instrument identifier.

        Returns:
            Formatted news block string.
        """
        if self._news_fetcher is not None:
            news: NewsContext = await self._news_fetcher(symbol)
            return news.to_text()
        await asyncio.sleep(0)
        return f"News for {symbol}: N/A (feed not configured)"
