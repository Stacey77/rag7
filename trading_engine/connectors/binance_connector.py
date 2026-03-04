"""Binance exchange connector using the python-binance library.

Defaults to Binance testnet for safety. Set ``BINANCE_TESTNET=false`` (or pass
``testnet=False``) to switch to the live environment.
"""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal
from typing import List, Optional

from loguru import logger

from shared.common.exceptions import ExchangeConnectionError, OrderRejectedError
from shared.models.trading_models import Order, OrderStatus, OrderType, Position, Side
from trading_engine.connectors.base_connector import BaseConnector


class BinanceConnector(BaseConnector):
    """Connector for Binance spot trading via python-binance.

    Args:
        api_key: Binance API key. Falls back to ``BINANCE_API_KEY`` env var.
        secret_key: Binance secret key. Falls back to ``BINANCE_SECRET_KEY`` env var.
        testnet: Use Binance testnet endpoints when True (default).
    """

    _TESTNET_REST = "https://testnet.binance.vision/api"
    _LIVE_REST = "https://api.binance.com/api"

    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        testnet: bool = True,
    ) -> None:
        env_testnet = os.getenv("BINANCE_TESTNET", "true").lower() not in ("false", "0", "no")
        self._api_key = api_key or os.getenv("BINANCE_API_KEY", "")
        self._secret_key = secret_key or os.getenv("BINANCE_SECRET_KEY", "")
        self._testnet = testnet and env_testnet
        self._connected = False
        self._client = None
        self._log = logger.bind(connector="binance", testnet=self._testnet)

    # ── Connection lifecycle ───────────────────────────────────────────────

    async def connect(self) -> bool:
        """Initialise the Binance REST client and test connectivity."""
        try:
            from binance.client import Client

            self._client = await asyncio.to_thread(
                Client,
                self._api_key,
                self._secret_key,
                testnet=self._testnet,
            )
            # Verify credentials
            await asyncio.to_thread(self._client.get_account)
            self._connected = True
            self._log.info("Connected to Binance", testnet=self._testnet)
            return True
        except Exception as exc:
            self._log.error("Failed to connect to Binance", error=str(exc))
            raise ExchangeConnectionError(f"Binance connection failed: {exc}") from exc

    async def disconnect(self) -> None:
        """Close the Binance client."""
        self._connected = False
        self._client = None
        self._log.info("Disconnected from Binance")

    # ── Order operations ───────────────────────────────────────────────────

    async def place_order(self, order: Order) -> str:
        """Submit a spot order to Binance."""
        if not self._connected or not self._client:
            raise ExchangeConnectionError("Not connected to Binance")
        try:
            side = "BUY" if order.side is Side.BUY else "SELL"

            if order.order_type is OrderType.MARKET:
                result = await asyncio.to_thread(
                    self._client.create_order,
                    symbol=order.symbol,
                    side=side,
                    type="MARKET",
                    quantity=float(order.quantity),
                )
            elif order.order_type is OrderType.LIMIT:
                if order.price is None:
                    raise OrderRejectedError(order.order_id, "Limit order requires a price")
                result = await asyncio.to_thread(
                    self._client.create_order,
                    symbol=order.symbol,
                    side=side,
                    type="LIMIT",
                    timeInForce=order.time_in_force.value,
                    quantity=float(order.quantity),
                    price=float(order.price),
                )
            else:
                raise OrderRejectedError(
                    order.order_id,
                    f"Unsupported order type {order.order_type} for Binance",
                )

            exchange_id = str(result["orderId"])
            self._log.info(
                "Order submitted to Binance",
                order_id=order.order_id,
                exchange_id=exchange_id,
            )
            return exchange_id
        except OrderRejectedError:
            raise
        except Exception as exc:
            self._log.error("Failed to place order on Binance", error=str(exc))
            raise OrderRejectedError(order.order_id, str(exc)) from exc

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an open order on Binance."""
        if not self._connected or not self._client:
            raise ExchangeConnectionError("Not connected to Binance")
        try:
            await asyncio.to_thread(
                self._client.cancel_order, symbol=symbol, orderId=int(order_id)
            )
            self._log.info("Order cancelled on Binance", order_id=order_id)
            return True
        except Exception as exc:
            self._log.warning(
                "Failed to cancel order on Binance", order_id=order_id, error=str(exc)
            )
            return False

    async def get_order(self, order_id: str, symbol: str) -> Optional[Order]:
        """Fetch an order from Binance."""
        if not self._connected or not self._client:
            raise ExchangeConnectionError("Not connected to Binance")
        try:
            raw = await asyncio.to_thread(
                self._client.get_order, symbol=symbol, orderId=int(order_id)
            )
            return self._convert_order(raw)
        except Exception as exc:
            self._log.warning(
                "Failed to fetch order from Binance", order_id=order_id, error=str(exc)
            )
            return None

    async def get_positions(self) -> List[Position]:
        """Return non-zero asset balances as pseudo-positions.

        Binance spot has no concept of positions; this returns assets with
        a non-zero free or locked balance as Position objects.
        """
        if not self._connected or not self._client:
            raise ExchangeConnectionError("Not connected to Binance")
        try:
            account = await asyncio.to_thread(self._client.get_account)
            positions: List[Position] = []
            for asset in account.get("balances", []):
                qty = Decimal(str(asset.get("free", "0"))) + Decimal(
                    str(asset.get("locked", "0"))
                )
                if qty > Decimal("0") and asset["asset"] != "USDT":
                    positions.append(
                        Position(
                            symbol=f"{asset['asset']}USDT",
                            side=Side.BUY,
                            quantity=qty,
                            average_entry_price=Decimal("1"),  # No entry price from spot balance
                        )
                    )
            return positions
        except Exception as exc:
            self._log.error("Failed to fetch balances from Binance", error=str(exc))
            raise ExchangeConnectionError(f"Failed to fetch positions: {exc}") from exc

    async def get_account_balance(self) -> dict:
        """Retrieve USDT and BTC balances from Binance."""
        if not self._connected or not self._client:
            raise ExchangeConnectionError("Not connected to Binance")
        account = await asyncio.to_thread(self._client.get_account)
        balances = {
            b["asset"]: {"free": b["free"], "locked": b["locked"]}
            for b in account.get("balances", [])
            if Decimal(b["free"]) > Decimal("0") or Decimal(b["locked"]) > Decimal("0")
        }
        return balances

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._connected

    @property
    def exchange_name(self) -> str:
        """Return exchange name."""
        return "binance"

    # ── Conversion helpers ─────────────────────────────────────────────────

    def _convert_order(self, raw: dict) -> Order:
        """Convert a Binance REST order dict to our Order model."""
        status_map = {
            "NEW": OrderStatus.SUBMITTED,
            "PARTIALLY_FILLED": OrderStatus.PARTIALLY_FILLED,
            "FILLED": OrderStatus.FILLED,
            "CANCELED": OrderStatus.CANCELLED,
            "REJECTED": OrderStatus.REJECTED,
            "EXPIRED": OrderStatus.EXPIRED,
        }
        status = status_map.get(raw.get("status", ""), OrderStatus.PENDING)
        side = Side.BUY if raw.get("side", "").upper() == "BUY" else Side.SELL
        order_type = (
            OrderType.MARKET if raw.get("type", "").upper() == "MARKET" else OrderType.LIMIT
        )
        qty = Decimal(str(raw.get("origQty", "0")))
        price_str = raw.get("price", "0")
        price = Decimal(price_str) if price_str and Decimal(price_str) > 0 else None
        filled_qty = Decimal(str(raw.get("executedQty", "0")))
        avg_fill_str = raw.get("cummulativeQuoteQty", "0")
        avg_fill = (
            Decimal(avg_fill_str) / filled_qty
            if filled_qty > Decimal("0") and avg_fill_str
            else None
        )
        return Order(
            order_id=str(raw.get("clientOrderId", raw.get("orderId", ""))),
            exchange_order_id=str(raw.get("orderId", "")),
            symbol=raw.get("symbol", ""),
            side=side,
            order_type=order_type,
            quantity=qty if qty > Decimal("0") else Decimal("1"),
            price=price,
            status=status,
            filled_quantity=filled_qty,
            average_fill_price=avg_fill,
        )
