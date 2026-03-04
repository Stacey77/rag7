"""Abstract base class for exchange connectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from shared.models.trading_models import Order, Position


class BaseConnector(ABC):
    """Abstract base class that all exchange connectors must implement.

    Provides a uniform interface for order placement, position retrieval,
    account management, and market data subscription across different exchanges.
    """

    @abstractmethod
    async def connect(self) -> bool:
        """Establish a connection to the exchange.

        Returns:
            True if connection was successful, False otherwise.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnect from the exchange."""

    @abstractmethod
    async def place_order(self, order: Order) -> str:
        """Submit an order to the exchange.

        Args:
            order: The order to submit.

        Returns:
            Exchange-assigned order ID.

        Raises:
            OrderRejectedError: If the exchange rejects the order.
            ExchangeConnectionError: If the connection is unavailable.
        """

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an open order on the exchange.

        Args:
            order_id: The exchange order ID to cancel.
            symbol: The instrument symbol of the order.

        Returns:
            True if cancellation was successful.
        """

    @abstractmethod
    async def get_order(self, order_id: str, symbol: str) -> Optional[Order]:
        """Fetch the current state of an order from the exchange.

        Args:
            order_id: The exchange order ID.
            symbol: The instrument symbol.

        Returns:
            The Order with updated status, or None if not found.
        """

    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Retrieve all open positions from the exchange.

        Returns:
            List of open positions.
        """

    @abstractmethod
    async def get_account_balance(self) -> dict:
        """Retrieve account balance information.

        Returns:
            Dictionary with asset balances.
        """

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if the connector has an active connection."""

    @property
    @abstractmethod
    def exchange_name(self) -> str:
        """Return the name of the exchange this connector targets."""

    @property
    def is_paper_mode(self) -> bool:
        """Return True when the connector is operating in paper/simulation mode.

        Defaults to False.  Override in paper-trading connectors.
        """
        return False
