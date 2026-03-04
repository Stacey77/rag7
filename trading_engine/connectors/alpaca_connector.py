"""Alpaca Markets exchange connector using the alpaca-py library."""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal
from typing import List, Optional

from loguru import logger

from shared.common.exceptions import ExchangeConnectionError, OrderRejectedError
from shared.models.trading_models import (
    Fill, Order, OrderStatus, OrderType, Position, Side, TimeInForce,
)
from trading_engine.connectors.base_connector import BaseConnector


class AlpacaConnector(BaseConnector):
    """Connector for Alpaca Markets (stocks & crypto).

    Uses alpaca-py for both REST and streaming WebSocket interactions.
    Defaults to paper trading mode for safety.

    Args:
        api_key: Alpaca API key. Falls back to ``ALPACA_API_KEY`` env var.
        secret_key: Alpaca secret key. Falls back to ``ALPACA_SECRET_KEY`` env var.
        paper: When True, use Alpaca paper trading endpoint.
    """

    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        paper: bool = True,
    ) -> None:
        self._api_key = api_key or os.getenv("ALPACA_API_KEY", "")
        self._secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY", "")
        self._paper = paper
        self._connected = False
        self._trading_client = None
        self._log = logger.bind(connector="alpaca", paper=paper)

    async def connect(self) -> bool:
        """Initialize the Alpaca trading client."""
        try:
            from alpaca.trading.client import TradingClient

            self._trading_client = TradingClient(
                api_key=self._api_key,
                secret_key=self._secret_key,
                paper=self._paper,
            )
            account = await asyncio.to_thread(self._trading_client.get_account)
            self._connected = True
            self._log.info("Connected to Alpaca", account_id=account.id, paper=self._paper)
            return True
        except Exception as exc:
            self._log.error("Failed to connect to Alpaca", error=str(exc))
            raise ExchangeConnectionError(f"Alpaca connection failed: {exc}") from exc

    async def disconnect(self) -> None:
        """Close the Alpaca client connection."""
        self._connected = False
        self._trading_client = None
        self._log.info("Disconnected from Alpaca")

    async def place_order(self, order: Order) -> str:
        """Submit an order to Alpaca."""
        if not self._connected or not self._trading_client:
            raise ExchangeConnectionError("Not connected to Alpaca")
        try:
            from alpaca.trading.enums import OrderSide, TimeInForce as AlpacaTIF
            from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest

            side = OrderSide.BUY if order.side is Side.BUY else OrderSide.SELL
            tif_map = {
                TimeInForce.GTC: AlpacaTIF.GTC,
                TimeInForce.IOC: AlpacaTIF.IOC,
                TimeInForce.FOK: AlpacaTIF.FOK,
                TimeInForce.GTD: AlpacaTIF.GTC,
            }
            tif = tif_map.get(order.time_in_force, AlpacaTIF.GTC)

            if order.order_type is OrderType.MARKET:
                req = MarketOrderRequest(
                    symbol=order.symbol,
                    qty=float(order.quantity),
                    side=side,
                    time_in_force=tif,
                )
            elif order.order_type is OrderType.LIMIT:
                req = LimitOrderRequest(
                    symbol=order.symbol,
                    qty=float(order.quantity),
                    side=side,
                    time_in_force=tif,
                    limit_price=float(order.price),  # type: ignore[arg-type]
                )
            else:
                raise OrderRejectedError(
                    order.order_id,
                    f"Unsupported order type {order.order_type} for Alpaca",
                )

            submitted = await asyncio.to_thread(self._trading_client.submit_order, req)
            exchange_id = str(submitted.id)
            self._log.info(
                "Order submitted to Alpaca",
                order_id=order.order_id,
                exchange_id=exchange_id,
            )
            return exchange_id
        except OrderRejectedError:
            raise
        except Exception as exc:
            self._log.error("Failed to place order on Alpaca", error=str(exc))
            raise OrderRejectedError(order.order_id, str(exc)) from exc

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order on Alpaca."""
        if not self._connected or not self._trading_client:
            raise ExchangeConnectionError("Not connected to Alpaca")
        try:
            import uuid

            await asyncio.to_thread(
                self._trading_client.cancel_order_by_id, uuid.UUID(order_id)
            )
            self._log.info("Order cancelled on Alpaca", order_id=order_id)
            return True
        except Exception as exc:
            self._log.warning(
                "Failed to cancel order on Alpaca", order_id=order_id, error=str(exc)
            )
            return False

    async def get_order(self, order_id: str, symbol: str) -> Optional[Order]:
        """Fetch an order from Alpaca."""
        if not self._connected or not self._trading_client:
            raise ExchangeConnectionError("Not connected to Alpaca")
        try:
            import uuid

            alpaca_order = await asyncio.to_thread(
                self._trading_client.get_order_by_id, uuid.UUID(order_id)
            )
            return self._convert_order(alpaca_order)
        except Exception as exc:
            self._log.warning(
                "Failed to fetch order from Alpaca", order_id=order_id, error=str(exc)
            )
            return None

    async def get_positions(self) -> List[Position]:
        """Get all open positions from Alpaca."""
        if not self._connected or not self._trading_client:
            raise ExchangeConnectionError("Not connected to Alpaca")
        try:
            positions = await asyncio.to_thread(self._trading_client.get_all_positions)
            return [self._convert_position(p) for p in positions]
        except Exception as exc:
            self._log.error("Failed to fetch positions from Alpaca", error=str(exc))
            raise ExchangeConnectionError(f"Failed to fetch positions: {exc}") from exc

    async def get_account_balance(self) -> dict:
        """Get account balance from Alpaca."""
        if not self._connected or not self._trading_client:
            raise ExchangeConnectionError("Not connected to Alpaca")
        account = await asyncio.to_thread(self._trading_client.get_account)
        return {
            "buying_power": str(account.buying_power),
            "cash": str(account.cash),
            "portfolio_value": str(account.portfolio_value),
            "equity": str(account.equity),
            "currency": "USD",
        }

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._connected

    @property
    def exchange_name(self) -> str:
        """Return exchange name."""
        return "alpaca"

    # ── Conversion helpers ─────────────────────────────────────────────────

    def _convert_order(self, alpaca_order: object) -> Order:
        """Convert an Alpaca order object to our Order model."""
        status_map = {
            "new": OrderStatus.SUBMITTED,
            "accepted": OrderStatus.ACCEPTED,
            "partially_filled": OrderStatus.PARTIALLY_FILLED,
            "filled": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELLED,
            "rejected": OrderStatus.REJECTED,
            "expired": OrderStatus.EXPIRED,
            "pending_new": OrderStatus.PENDING,
        }
        ao = alpaca_order
        status = status_map.get(str(ao.status).lower(), OrderStatus.PENDING)
        side = Side.BUY if str(ao.side).lower() in ("buy", "orderside.buy") else Side.SELL
        order_type = (
            OrderType.MARKET
            if str(ao.order_type).lower() in ("market", "ordertype.market")
            else OrderType.LIMIT
        )
        qty = Decimal(str(ao.qty or "0"))
        price = Decimal(str(ao.limit_price)) if ao.limit_price else None
        filled_qty = Decimal(str(ao.filled_qty or "0"))
        avg_fill = Decimal(str(ao.filled_avg_price)) if ao.filled_avg_price else None
        return Order(
            order_id=str(ao.client_order_id) if ao.client_order_id else str(ao.id),
            exchange_order_id=str(ao.id),
            symbol=ao.symbol,
            side=side,
            order_type=order_type,
            quantity=qty if qty > Decimal("0") else Decimal("1"),
            price=price,
            status=status,
            filled_quantity=filled_qty,
            average_fill_price=avg_fill,
        )

    def _convert_position(self, alpaca_position: object) -> Position:
        """Convert an Alpaca position object to our Position model."""
        ap = alpaca_position
        side = Side.BUY if str(ap.side).lower() in ("long", "positionside.long") else Side.SELL
        qty = abs(Decimal(str(ap.qty or "1")))
        avg_entry = Decimal(str(ap.avg_entry_price or "0"))
        unrealised = Decimal(str(ap.unrealized_pl or "0"))
        return Position(
            symbol=ap.symbol,
            side=side,
            quantity=qty if qty > Decimal("0") else Decimal("1"),
            average_entry_price=avg_entry if avg_entry > Decimal("0") else Decimal("1"),
            unrealised_pnl=unrealised,
        )
