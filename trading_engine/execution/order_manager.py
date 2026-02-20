"""Order lifecycle manager.

Wraps an exchange connector with an in-process order registry, state
transition validation, and structured logging.  All public methods are
async so they compose naturally with the rest of the async stack.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

from loguru import logger

from shared.common.exceptions import (
    ExchangeConnectionError,
    OrderNotFoundError,
    OrderRejectedError,
)
from shared.models.trading_models import Order, OrderStatus
from trading_engine.connectors.base_connector import BaseConnector


class OrderManager:
    """Manages the full lifecycle of trading orders.

    Maintains an internal registry keyed by ``order_id`` and delegates
    exchange operations to the supplied :class:`BaseConnector`.

    Args:
        connector: An initialised exchange connector.
    """

    def __init__(self, connector: BaseConnector) -> None:
        self._connector = connector
        self._orders: Dict[str, Order] = {}
        self._lock = asyncio.Lock()
        self._log = logger.bind(component="order_manager")

    # ── Public API ─────────────────────────────────────────────────────────

    async def submit_order(self, order: Order) -> str:
        """Submit an order to the exchange and register it locally.

        Args:
            order: The order to submit.

        Returns:
            Exchange-assigned order ID.

        Raises:
            ExchangeConnectionError: Connector is not connected.
            OrderRejectedError: Exchange rejected the order.
        """
        self._log.info(
            "Submitting order",
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=str(order.quantity),
        )

        async with self._lock:
            # Transition to SUBMITTED before sending to exchange
            updated = order.model_copy(
                update={
                    "status": OrderStatus.SUBMITTED,
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            self._orders[updated.order_id] = updated

        try:
            exchange_id = await self._connector.place_order(updated)
        except (ExchangeConnectionError, OrderRejectedError):
            async with self._lock:
                self._orders[updated.order_id] = updated.model_copy(
                    update={
                        "status": OrderStatus.REJECTED,
                        "updated_at": datetime.now(timezone.utc),
                    }
                )
            raise

        async with self._lock:
            self._orders[updated.order_id] = updated.model_copy(
                update={
                    "exchange_order_id": exchange_id,
                    "status": OrderStatus.ACCEPTED,
                    "updated_at": datetime.now(timezone.utc),
                }
            )

        self._log.info(
            "Order accepted by exchange",
            order_id=updated.order_id,
            exchange_id=exchange_id,
        )
        return exchange_id

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order.

        Args:
            order_id: Internal order ID (not exchange ID).

        Returns:
            True if cancellation was acknowledged.

        Raises:
            OrderNotFoundError: No order with that ID in the registry.
        """
        async with self._lock:
            order = self._orders.get(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        if not order.is_open:
            self._log.warning(
                "Cannot cancel a non-open order",
                order_id=order_id,
                status=order.status,
            )
            return False

        exchange_id = order.exchange_order_id or order_id
        cancelled = await self._connector.cancel_order(exchange_id, order.symbol)

        if cancelled:
            async with self._lock:
                self._orders[order_id] = order.model_copy(
                    update={
                        "status": OrderStatus.CANCELLED,
                        "updated_at": datetime.now(timezone.utc),
                    }
                )
            self._log.info("Order cancelled", order_id=order_id)
        else:
            self._log.warning("Cancellation returned False", order_id=order_id)

        return cancelled

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Return the current order state from the registry.

        Refreshes from the exchange if an exchange order ID is available.

        Args:
            order_id: Internal order ID.

        Returns:
            Current Order, or None if not found.
        """
        async with self._lock:
            order = self._orders.get(order_id)

        if order is None:
            return None

        # Refresh from exchange if we have an exchange ID
        if order.exchange_order_id and order.is_open:
            refreshed = await self._connector.get_order(order.exchange_order_id, order.symbol)
            if refreshed is not None:
                refreshed = refreshed.model_copy(update={"order_id": order_id})
                async with self._lock:
                    self._orders[order_id] = refreshed
                return refreshed

        return order

    async def get_open_orders(self) -> List[Order]:
        """Return all open orders currently tracked by the manager.

        Returns:
            List of orders with an open status.
        """
        async with self._lock:
            return [o for o in self._orders.values() if o.is_open]

    async def get_all_orders(self) -> List[Order]:
        """Return all orders (open and closed) in the registry."""
        async with self._lock:
            return list(self._orders.values())

    def order_count(self) -> int:
        """Return the number of tracked orders.

        ``len()`` on a dict is atomic under the GIL, so this is safe to call
        from any async task without acquiring the lock.
        """
        return len(self._orders)
