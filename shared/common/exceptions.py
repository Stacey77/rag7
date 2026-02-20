"""Domain exceptions for the AGI Trading Platform.

All platform exceptions inherit from ``TradingPlatformError`` so callers can
catch the entire hierarchy with a single ``except TradingPlatformError`` clause
when needed.
"""

from __future__ import annotations


class TradingPlatformError(Exception):
    """Base exception for all platform errors."""


# ── Exchange / Connectivity ────────────────────────────────────────────────


class ExchangeConnectionError(TradingPlatformError):
    """Raised when a connector cannot reach or authenticate with an exchange."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ExchangeRateLimitError(TradingPlatformError):
    """Raised when the exchange rate-limit is breached."""

    def __init__(self, exchange: str, retry_after_seconds: float = 0.0) -> None:
        super().__init__(f"Rate limit hit on {exchange}. Retry after {retry_after_seconds}s.")
        self.exchange = exchange
        self.retry_after_seconds = retry_after_seconds


# ── Order Management ───────────────────────────────────────────────────────


class OrderRejectedError(TradingPlatformError):
    """Raised when an exchange rejects an order submission."""

    def __init__(self, order_id: str, reason: str) -> None:
        super().__init__(f"Order {order_id} rejected: {reason}")
        self.order_id = order_id
        self.reason = reason


class OrderNotFoundError(TradingPlatformError):
    """Raised when an order cannot be located in the registry or exchange."""

    def __init__(self, order_id: str) -> None:
        super().__init__(f"Order {order_id} not found.")
        self.order_id = order_id


class OrderCancellationError(TradingPlatformError):
    """Raised when an order cancellation fails."""

    def __init__(self, order_id: str, reason: str) -> None:
        super().__init__(f"Cannot cancel order {order_id}: {reason}")
        self.order_id = order_id
        self.reason = reason


# ── Risk Management ────────────────────────────────────────────────────────


class RiskLimitBreachedError(TradingPlatformError):
    """Raised when a proposed trade violates a pre-trade risk limit."""

    def __init__(self, limit_name: str, value: float, limit: float) -> None:
        super().__init__(
            f"Risk limit '{limit_name}' breached: {value:.4f} exceeds {limit:.4f}."
        )
        self.limit_name = limit_name
        self.value = value
        self.limit = limit


# ── Data / Storage ─────────────────────────────────────────────────────────


class DataIngestionError(TradingPlatformError):
    """Raised when market data ingestion fails."""


class StorageError(TradingPlatformError):
    """Raised when a database or cache operation fails."""


# ── Configuration ──────────────────────────────────────────────────────────


class ConfigurationError(TradingPlatformError):
    """Raised when the platform configuration is invalid or missing."""
