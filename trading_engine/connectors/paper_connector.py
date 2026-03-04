"""Paper (in-memory simulation) exchange connector.

Used for local development and testing when no real exchange credentials are
configured.  All operations succeed instantly with simulated fills.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from loguru import logger

from shared.models.trading_models import (
    Fill,
    Order,
    OrderStatus,
    OrderType,
    Position,
    Side,
)
from trading_engine.connectors.base_connector import BaseConnector

#: Fallback fill price for MARKET orders with no price attached.
#: Only used in paper simulation; real connectors always receive a fill price
#: from the exchange.  Pass a ``price`` on MARKET orders for accurate results.
_DEFAULT_FILL_PRICE = Decimal("1.00")


class PaperConnector(BaseConnector):
    """Simulated exchange connector for paper trading.

    Accepts all orders, generates synthetic fills for MARKET orders, and
    maintains a simple in-memory position ledger.  No external network calls
    are made.

    Args:
        slippage_bps: Simulated slippage in basis-points applied to MARKET
            fills (default 5 bps = 0.05 %).
    """

    def __init__(self, slippage_bps: float = 5.0) -> None:
        self._slippage_factor = Decimal(str(slippage_bps)) / Decimal("10000")
        self._orders: Dict[str, Order] = {}
        self._positions: Dict[str, Position] = {}
        self._connected = False
        self._log = logger.bind(connector="paper")

    # ── BaseConnector interface ────────────────────────────────────────────

    async def connect(self) -> bool:
        """Paper connector is always available."""
        self._connected = True
        self._log.info("Paper connector ready (no external connection needed)")
        return True

    async def disconnect(self) -> None:
        """Mark as disconnected."""
        self._connected = False
        self._log.info("Paper connector disconnected")

    async def place_order(self, order: Order) -> str:
        """Accept the order and generate a synthetic fill for MARKET orders.

        Args:
            order: The order to simulate.

        Returns:
            Simulated exchange-assigned order ID.
        """
        exchange_id = f"paper-{uuid.uuid4().hex[:12]}"
        self._log.info(
            "Paper order placed",
            order_id=order.order_id,
            exchange_id=exchange_id,
            symbol=order.symbol,
            side=order.side,
            quantity=str(order.quantity),
        )
        self._orders[exchange_id] = order.model_copy(
            update={
                "exchange_order_id": exchange_id,
                "status": OrderStatus.ACCEPTED,
                "updated_at": datetime.now(timezone.utc),
            }
        )

        if order.order_type is OrderType.MARKET:
            self._simulate_fill(exchange_id, order)

        return exchange_id

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Mark a simulated order as cancelled.

        Args:
            order_id: Exchange order ID (paper-…).
            symbol: Instrument symbol (unused in simulation).

        Returns:
            True — paper cancellations always succeed.
        """
        if order_id in self._orders:
            self._orders[order_id] = self._orders[order_id].model_copy(
                update={
                    "status": OrderStatus.CANCELLED,
                    "updated_at": datetime.now(timezone.utc),
                }
            )
        self._log.info("Paper order cancelled", order_id=order_id)
        return True

    async def get_order(self, order_id: str, symbol: str) -> Optional[Order]:
        """Return the simulated order state.

        Args:
            order_id: Exchange order ID.
            symbol: Instrument symbol (unused).

        Returns:
            Current Order state, or None if not found.
        """
        return self._orders.get(order_id)

    async def get_positions(self) -> List[Position]:
        """Return all currently simulated open positions."""
        return list(self._positions.values())

    async def get_account_balance(self) -> dict:
        """Return a mock account balance.

        Returns:
            Dictionary with a fixed simulated USD balance.
        """
        return {
            "USD": "1000000.00",
            "currency": "USD",
            "note": "paper-trading — simulated balance",
        }

    @property
    def is_connected(self) -> bool:
        """Return True when the paper connector is ready."""
        return self._connected

    @property
    def exchange_name(self) -> str:
        """Exchange name for the paper connector."""
        return "paper"

    @property
    def is_paper_mode(self) -> bool:
        """Paper connector always operates in simulation mode."""
        return True

    # ── Internal helpers ──────────────────────────────────────────────────

    def _simulate_fill(self, exchange_id: str, order: Order) -> None:
        """Apply a synthetic fill to a MARKET order.

        Uses the order price when available, otherwise falls back to a
        placeholder price of 1.00 USD.  Slippage is applied in the
        direction of the trade (buy fills slightly higher, sell slightly lower).
        """
        base_price = order.price or _DEFAULT_FILL_PRICE
        if order.side is Side.BUY:
            fill_price = base_price * (1 + self._slippage_factor)
        else:
            fill_price = base_price * (1 - self._slippage_factor)

        fill = Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price.quantize(Decimal("0.01")),
        )

        filled_order = self._orders[exchange_id].model_copy(
            update={
                "status": OrderStatus.FILLED,
                "filled_quantity": order.quantity,
                "average_fill_price": fill.price,
                "fills": [fill],
                "updated_at": datetime.now(timezone.utc),
            }
        )
        self._orders[exchange_id] = filled_order
        self._log.debug(
            "Paper fill simulated",
            symbol=order.symbol,
            quantity=str(order.quantity),
            price=str(fill.price),
        )
