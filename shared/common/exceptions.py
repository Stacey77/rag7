"""Custom exception hierarchy for the trading platform.

All platform-specific errors derive from :class:`TradingPlatformError` so
callers can catch the entire family with a single ``except`` clause.

Hierarchy::

    TradingPlatformError
    ├── ConfigurationError
    ├── AGIError
    │   ├── ModelNotAvailableError
    │   └── InferenceError
    ├── TradingError
    │   ├── OrderError
    │   │   ├── OrderNotFoundError
    │   │   ├── OrderRejectedError
    │   │   └── DuplicateOrderError
    │   ├── PositionError
    │   │   └── InsufficientFundsError
    │   └── RiskLimitError
    │       ├── MaxDrawdownError
    │       └── PositionSizeLimitError
    ├── DataError
    │   ├── MarketDataError
    │   │   └── StaleDataError
    │   └── ValidationError
    ├── ConnectionError
    │   ├── BrokerConnectionError
    │   └── ExchangeConnectionError
    └── AuthenticationError
"""

from __future__ import annotations

from typing import Any


class TradingPlatformError(Exception):
    """Base class for all trading-platform exceptions.

    Args:
        message: Human-readable error description.
        code: Optional machine-readable error code for structured handling.
        context: Optional mapping of extra diagnostic key-value pairs.
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context: dict[str, Any] = context or {}

    def __repr__(self) -> str:  # noqa: D105
        return (
            f"{type(self).__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"context={self.context!r})"
        )


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class ConfigurationError(TradingPlatformError):
    """Raised when configuration is missing or invalid."""


# ---------------------------------------------------------------------------
# AGI / ML subsystem
# ---------------------------------------------------------------------------


class AGIError(TradingPlatformError):
    """Base class for AGI/ML orchestration errors."""


class ModelNotAvailableError(AGIError):
    """Raised when a required model is not loaded or unreachable."""


class InferenceError(AGIError):
    """Raised when model inference fails or returns an unusable result."""


# ---------------------------------------------------------------------------
# Trading subsystem
# ---------------------------------------------------------------------------


class TradingError(TradingPlatformError):
    """Base class for trading-execution errors."""


class OrderError(TradingError):
    """Base class for order-lifecycle errors."""


class OrderNotFoundError(OrderError):
    """Raised when an order ID cannot be located."""


class OrderRejectedError(OrderError):
    """Raised when an exchange or broker rejects an order.

    Args:
        order_id: The order identifier that was rejected.
        reason: Exchange/broker rejection reason string.
        **kwargs: Forwarded to :class:`TradingPlatformError`.
    """

    def __init__(self, order_id: str, reason: str, **kwargs: Any) -> None:
        super().__init__(
            f"Order {order_id!r} rejected: {reason}",
            context={"order_id": order_id, "reason": reason},
            **kwargs,
        )
        self.order_id = order_id
        self.reason = reason


class DuplicateOrderError(OrderError):
    """Raised on an attempt to submit an order with an already-used client ID."""


class PositionError(TradingError):
    """Base class for position-management errors."""


class InsufficientFundsError(PositionError):
    """Raised when available capital is below what an order requires."""


class RiskLimitError(TradingError):
    """Raised when a risk limit is breached."""


class MaxDrawdownError(RiskLimitError):
    """Raised when the portfolio max-drawdown threshold is exceeded."""


class PositionSizeLimitError(RiskLimitError):
    """Raised when a single position would exceed the configured size limit."""


# ---------------------------------------------------------------------------
# Data subsystem
# ---------------------------------------------------------------------------


class DataError(TradingPlatformError):
    """Base class for data-related errors."""


class MarketDataError(DataError):
    """Raised when market-data retrieval or parsing fails."""


class StaleDataError(MarketDataError):
    """Raised when market data is older than the acceptable staleness threshold."""


class ValidationError(DataError):
    """Raised when a data model fails validation.

    Args:
        field: The field name that failed validation.
        value: The offending value.
        **kwargs: Forwarded to :class:`TradingPlatformError`.
    """

    def __init__(self, field: str, value: Any, **kwargs: Any) -> None:
        super().__init__(
            f"Validation failed for field {field!r}: {value!r}",
            context={"field": field, "value": value},
            **kwargs,
        )
        self.field = field
        self.value = value


# ---------------------------------------------------------------------------
# Connectivity
# ---------------------------------------------------------------------------


class ConnectivityError(TradingPlatformError):
    """Base class for connection / transport errors."""


class BrokerConnectionError(ConnectivityError):
    """Raised when the connection to a broker is lost or unavailable."""


class ExchangeConnectionError(ConnectivityError):
    """Raised when the connection to a crypto/equity exchange fails."""


# ---------------------------------------------------------------------------
# Authentication / authorisation
# ---------------------------------------------------------------------------


class AuthenticationError(TradingPlatformError):
    """Raised on authentication or API-key verification failures."""
