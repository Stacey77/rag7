"""REST API router for the trading engine.

Exposes two groups of endpoints:

* ``/api/v1/orders``   — submit, query, and cancel orders
* ``/api/v1/portfolio`` — read portfolio state and positions
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from shared.common.exceptions import OrderNotFoundError, OrderRejectedError
from shared.models.ai_models import RiskAssessment
from shared.models.trading_models import (
    Order,
    OrderType,
    Portfolio,
    Position,
    Side,
    TimeInForce,
)

router = APIRouter(prefix="/api/v1", tags=["trading"])


# ── Dependency helpers ────────────────────────────────────────────────────


def _order_manager(request: Request):  # type: ignore[return]
    return request.app.state.order_manager


def _portfolio_manager(request: Request):  # type: ignore[return]
    return request.app.state.portfolio_manager


def _risk_engine(request: Request):  # type: ignore[return]
    return request.app.state.risk_engine


# ── Request schemas ───────────────────────────────────────────────────────


class PlaceOrderRequest(BaseModel):
    """Fields required to place a new order."""

    symbol: str = Field(..., description="Trading pair, e.g. 'BTCUSDT'.")
    side: Side = Field(..., description="BUY or SELL.")
    order_type: OrderType = Field(..., description="MARKET, LIMIT, etc.")
    quantity: Decimal = Field(..., gt=Decimal("0"), description="Order quantity.")
    price: Optional[Decimal] = Field(
        None, gt=Decimal("0"), description="Limit price (required for LIMIT orders)."
    )
    stop_price: Optional[Decimal] = Field(
        None, gt=Decimal("0"), description="Stop-trigger price."
    )
    time_in_force: TimeInForce = Field(TimeInForce.GTC, description="GTC, IOC, FOK, DAY.")
    client_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary client tags."
    )


# ── Response helpers ──────────────────────────────────────────────────────


def _order_to_dict(order: Order) -> dict:
    """Serialise an Order to a JSON-compatible dict."""
    return order.model_dump(mode="json")


def _position_to_dict(pos: Position) -> dict:
    """Serialise a Position to a JSON-compatible dict."""
    return pos.model_dump(mode="json")


def _portfolio_to_dict(portfolio: Portfolio) -> dict:
    """Serialise a Portfolio to a JSON-compatible dict."""
    d = portfolio.model_dump(mode="json")
    # Flatten computed properties for convenience
    d["drawdown_pct"] = portfolio.drawdown_pct
    d["unrealised_pnl"] = str(portfolio.unrealised_pnl)
    return d


# ── Order endpoints ───────────────────────────────────────────────────────


@router.post(
    "/orders",
    summary="Place a new order",
    response_description="Submitted order with risk assessment",
)
async def place_order(
    body: PlaceOrderRequest,
    request: Request,
) -> dict:
    """Run a pre-trade risk check then submit the order to the exchange.

    The response always includes the ``risk_assessment`` so callers can
    inspect why an order was rejected without needing a separate call.

    * **201 Created** — order submitted to the exchange successfully.
    * **200 OK** — order blocked by pre-trade risk checks (not submitted).
    * **400 Bad Request** — order rejected by the exchange.
    * **503 Service Unavailable** — exchange connector unavailable.

    Returns:
        dict with keys ``order``, ``risk_assessment``, and (when submitted)
        ``exchange_order_id``.
    """
    from fastapi.responses import JSONResponse

    om = _order_manager(request)
    pm = _portfolio_manager(request)
    re = _risk_engine(request)

    order = Order(
        symbol=body.symbol,
        side=body.side,
        order_type=body.order_type,
        quantity=body.quantity,
        price=body.price,
        stop_price=body.stop_price,
        time_in_force=body.time_in_force,
        client_metadata=body.client_metadata,
    )

    portfolio = await pm.get_portfolio()
    assessment: RiskAssessment = await re.evaluate(order, portfolio)

    if not assessment.is_approved:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "order": _order_to_dict(order),
                "risk_assessment": assessment.model_dump(mode="json"),
            },
        )

    try:
        exchange_id = await om.submit_order(order)
    except OrderRejectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "order_rejected", "reason": exc.reason, "order_id": exc.order_id},
        ) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "exchange_unavailable", "detail": str(exc)},
        ) from exc

    updated = await om.get_order(order.order_id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "order": _order_to_dict(updated or order),
            "exchange_order_id": exchange_id,
            "risk_assessment": assessment.model_dump(mode="json"),
        },
    )


@router.get(
    "/orders",
    summary="List open orders",
)
async def list_open_orders(request: Request) -> List[dict]:
    """Return all orders that are currently open (not yet filled/cancelled).

    Returns:
        List of open :class:`Order` objects serialised as dicts.
    """
    om = _order_manager(request)
    orders = await om.get_open_orders()
    return [_order_to_dict(o) for o in orders]


@router.get(
    "/orders/{order_id}",
    summary="Get a specific order",
)
async def get_order(order_id: str, request: Request) -> dict:
    """Retrieve a single order by its internal ID.

    Args:
        order_id: Internal (client-generated) order UUID.

    Raises:
        404: Order not found.
    """
    om = _order_manager(request)
    order = await om.get_order(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "order_not_found", "order_id": order_id},
        )
    return _order_to_dict(order)


@router.delete(
    "/orders/{order_id}",
    summary="Cancel an open order",
)
async def cancel_order(order_id: str, request: Request) -> dict:
    """Request cancellation of an open order.

    Args:
        order_id: Internal order UUID.

    Returns:
        ``{"cancelled": true, "order_id": "<id>"}``

    Raises:
        404: Order not found.
        409: Order is already in a terminal state.
    """
    om = _order_manager(request)
    try:
        cancelled = await om.cancel_order(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "order_not_found", "order_id": order_id},
        ) from exc

    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "order_not_cancellable", "order_id": order_id},
        )
    return {"cancelled": True, "order_id": order_id}


# ── Portfolio endpoints ───────────────────────────────────────────────────


@router.get(
    "/portfolio",
    summary="Get portfolio summary",
)
async def get_portfolio(request: Request) -> dict:
    """Return the current portfolio state including cash, equity, and P&L.

    Returns:
        Serialised :class:`Portfolio` with computed ``drawdown_pct``
        and ``unrealised_pnl`` fields appended.
    """
    pm = _portfolio_manager(request)
    portfolio = await pm.get_portfolio()
    return _portfolio_to_dict(portfolio)


@router.get(
    "/portfolio/positions",
    summary="List all open positions",
)
async def list_positions(request: Request) -> List[dict]:
    """Return all currently open positions.

    Returns:
        List of :class:`Position` objects serialised as dicts.
    """
    pm = _portfolio_manager(request)
    portfolio = await pm.get_portfolio()
    return [_position_to_dict(p) for p in portfolio.positions.values()]


@router.get(
    "/portfolio/positions/{symbol}",
    summary="Get a specific position",
)
async def get_position(symbol: str, request: Request) -> dict:
    """Return the open position for a specific instrument.

    Args:
        symbol: Instrument symbol, e.g. ``BTCUSDT``.

    Raises:
        404: No open position for that symbol.
    """
    pm = _portfolio_manager(request)
    position = await pm.get_position(symbol.upper())
    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "position_not_found", "symbol": symbol.upper()},
        )
    return _position_to_dict(position)
