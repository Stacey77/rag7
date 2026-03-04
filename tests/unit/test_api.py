"""Unit tests for the trading API router.

Uses FastAPI's ``TestClient`` (synchronous) together with pre-configured
``app.state`` mocks so no real exchange connections are needed.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from shared.models.ai_models import RiskAssessment
from shared.models.trading_models import (
    Fill,
    Order,
    OrderStatus,
    OrderType,
    Portfolio,
    Position,
    Side,
)
from trading_engine.portfolio.portfolio_manager import PortfolioManager
from trading_engine.risk_management.risk_engine import RiskEngine


# ── Helpers ───────────────────────────────────────────────────────────────


def _make_app(portfolio_manager, risk_engine, order_manager):
    """Build a FastAPI test app with services pre-loaded in state."""
    from fastapi import FastAPI
    from trading_engine.api.router import router as trading_router

    app = FastAPI()
    app.state.portfolio_manager = portfolio_manager
    app.state.risk_engine = risk_engine
    app.state.order_manager = order_manager
    app.include_router(trading_router)
    return app


def _approved_assessment(symbol: str = "BTCUSDT") -> RiskAssessment:
    return RiskAssessment(
        symbol=symbol,
        proposed_quantity=Decimal("0.01"),
        proposed_notional_usd=Decimal("450"),
        current_drawdown_pct=0.0,
        is_approved=True,
        risk_score=0.1,
    )


def _rejected_assessment(symbol: str = "BTCUSDT") -> RiskAssessment:
    return RiskAssessment(
        symbol=symbol,
        proposed_quantity=Decimal("9999"),
        proposed_notional_usd=Decimal("99990000"),
        current_drawdown_pct=0.0,
        is_approved=False,
        risk_score=0.9,
        rejection_reasons=["Order notional exceeds max order size"],
    )


def _sample_order(symbol: str = "BTCUSDT") -> Order:
    return Order(
        symbol=symbol,
        side=Side.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.01"),
        status=OrderStatus.ACCEPTED,
        exchange_order_id="paper-abc123",
    )


def _sample_position(symbol: str = "BTCUSDT") -> Position:
    return Position(
        symbol=symbol,
        side=Side.BUY,
        quantity=Decimal("0.5"),
        average_entry_price=Decimal("45000"),
        current_price=Decimal("47000"),
        unrealised_pnl=Decimal("1000"),
    )


def _empty_portfolio() -> Portfolio:
    return Portfolio(
        account_id="test",
        cash_balance=Decimal("100000"),
        total_equity=Decimal("100000"),
        peak_equity=Decimal("100000"),
    )


def _portfolio_with_position() -> Portfolio:
    pos = _sample_position()
    return Portfolio(
        account_id="test",
        positions={"BTCUSDT": pos},
        cash_balance=Decimal("77500"),
        total_equity=Decimal("100000"),
        peak_equity=Decimal("100000"),
    )


# ── Test classes ──────────────────────────────────────────────────────────


class TestPlaceOrder:
    """POST /api/v1/orders"""

    @pytest.fixture
    def client_approved(self):
        order = _sample_order()
        pm = AsyncMock(spec=PortfolioManager)
        pm.get_portfolio = AsyncMock(return_value=_empty_portfolio())
        re = AsyncMock(spec=RiskEngine)
        re.evaluate = AsyncMock(return_value=_approved_assessment())
        om = AsyncMock()
        om.submit_order = AsyncMock(return_value="paper-abc123")
        om.get_order = AsyncMock(return_value=order)
        return TestClient(_make_app(pm, re, om))

    @pytest.fixture
    def client_rejected(self):
        pm = AsyncMock(spec=PortfolioManager)
        pm.get_portfolio = AsyncMock(return_value=_empty_portfolio())
        re = AsyncMock(spec=RiskEngine)
        re.evaluate = AsyncMock(return_value=_rejected_assessment())
        om = AsyncMock()
        return TestClient(_make_app(pm, re, om))

    def test_place_market_order_approved(self, client_approved):
        """Approved order returns 201 with order and risk_assessment."""
        resp = client_approved.post(
            "/api/v1/orders",
            json={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "MARKET",
                "quantity": "0.01",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "order" in body
        assert "risk_assessment" in body
        assert body["risk_assessment"]["is_approved"] is True
        assert body["exchange_order_id"] == "paper-abc123"

    def test_place_order_risk_rejected_returns_200_with_assessment(self, client_rejected):
        """Risk-rejected order returns 200 (not 4xx) with is_approved=false."""
        resp = client_rejected.post(
            "/api/v1/orders",
            json={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "MARKET",
                "quantity": "9999",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["risk_assessment"]["is_approved"] is False
        assert len(body["risk_assessment"]["rejection_reasons"]) > 0

    def test_place_order_missing_symbol_returns_422(self, client_approved):
        """Missing required field returns 422 Unprocessable Entity."""
        resp = client_approved.post(
            "/api/v1/orders",
            json={"side": "BUY", "order_type": "MARKET", "quantity": "0.01"},
        )
        assert resp.status_code == 422

    def test_place_order_invalid_side_returns_422(self, client_approved):
        """Invalid enum value returns 422."""
        resp = client_approved.post(
            "/api/v1/orders",
            json={
                "symbol": "BTCUSDT",
                "side": "INVALID",
                "order_type": "MARKET",
                "quantity": "0.01",
            },
        )
        assert resp.status_code == 422


class TestListOrders:
    """GET /api/v1/orders"""

    @pytest.fixture
    def client(self):
        pm = AsyncMock(spec=PortfolioManager)
        re = AsyncMock(spec=RiskEngine)
        om = AsyncMock()
        om.get_open_orders = AsyncMock(return_value=[_sample_order()])
        return TestClient(_make_app(pm, re, om))

    @pytest.fixture
    def client_empty(self):
        pm = AsyncMock(spec=PortfolioManager)
        re = AsyncMock(spec=RiskEngine)
        om = AsyncMock()
        om.get_open_orders = AsyncMock(return_value=[])
        return TestClient(_make_app(pm, re, om))

    def test_list_orders_returns_list(self, client):
        """Returns a list of open orders."""
        resp = client.get("/api/v1/orders")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) == 1

    def test_list_orders_empty(self, client_empty):
        """Returns an empty list when no orders are open."""
        resp = client_empty.get("/api/v1/orders")
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetOrder:
    """GET /api/v1/orders/{order_id}"""

    @pytest.fixture
    def client(self):
        order = _sample_order()
        om = AsyncMock()
        om.get_order = AsyncMock(return_value=order)
        pm = AsyncMock(spec=PortfolioManager)
        re = AsyncMock(spec=RiskEngine)
        self._order_id = order.order_id
        return TestClient(_make_app(pm, re, om))

    @pytest.fixture
    def client_not_found(self):
        om = AsyncMock()
        om.get_order = AsyncMock(return_value=None)
        pm = AsyncMock(spec=PortfolioManager)
        re = AsyncMock(spec=RiskEngine)
        return TestClient(_make_app(pm, re, om))

    def test_get_existing_order(self, client):
        """Returns 200 with order data for a known order_id."""
        resp = client.get(f"/api/v1/orders/{self._order_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["order_id"] == self._order_id

    def test_get_unknown_order_returns_404(self, client_not_found):
        """Returns 404 for an unknown order_id."""
        resp = client_not_found.get("/api/v1/orders/nonexistent-id")
        assert resp.status_code == 404
        assert resp.json()["detail"]["error"] == "order_not_found"


class TestCancelOrder:
    """DELETE /api/v1/orders/{order_id}"""

    @pytest.fixture
    def client_success(self):
        om = AsyncMock()
        om.cancel_order = AsyncMock(return_value=True)
        pm = AsyncMock(spec=PortfolioManager)
        re = AsyncMock(spec=RiskEngine)
        return TestClient(_make_app(pm, re, om))

    @pytest.fixture
    def client_not_cancellable(self):
        om = AsyncMock()
        om.cancel_order = AsyncMock(return_value=False)
        pm = AsyncMock(spec=PortfolioManager)
        re = AsyncMock(spec=RiskEngine)
        return TestClient(_make_app(pm, re, om))

    @pytest.fixture
    def client_not_found(self):
        from shared.common.exceptions import OrderNotFoundError
        om = AsyncMock()
        om.cancel_order = AsyncMock(side_effect=OrderNotFoundError("bad-id"))
        pm = AsyncMock(spec=PortfolioManager)
        re = AsyncMock(spec=RiskEngine)
        return TestClient(_make_app(pm, re, om))

    def test_cancel_order_success(self, client_success):
        """Returns 200 with cancelled=true."""
        resp = client_success.delete("/api/v1/orders/some-order-id")
        assert resp.status_code == 200
        assert resp.json()["cancelled"] is True

    def test_cancel_non_cancellable_returns_409(self, client_not_cancellable):
        """Returns 409 when the order cannot be cancelled."""
        resp = client_not_cancellable.delete("/api/v1/orders/some-order-id")
        assert resp.status_code == 409

    def test_cancel_not_found_returns_404(self, client_not_found):
        """Returns 404 when the order does not exist."""
        resp = client_not_found.delete("/api/v1/orders/bad-id")
        assert resp.status_code == 404


class TestPortfolioEndpoints:
    """GET /api/v1/portfolio and sub-routes"""

    @pytest.fixture
    def client_with_position(self):
        pm = AsyncMock(spec=PortfolioManager)
        pm.get_portfolio = AsyncMock(return_value=_portfolio_with_position())
        pm.get_position = AsyncMock(return_value=_sample_position())
        re = AsyncMock(spec=RiskEngine)
        om = AsyncMock()
        return TestClient(_make_app(pm, re, om))

    @pytest.fixture
    def client_empty(self):
        pm = AsyncMock(spec=PortfolioManager)
        pm.get_portfolio = AsyncMock(return_value=_empty_portfolio())
        pm.get_position = AsyncMock(return_value=None)
        re = AsyncMock(spec=RiskEngine)
        om = AsyncMock()
        return TestClient(_make_app(pm, re, om))

    def test_get_portfolio_returns_200(self, client_with_position):
        """GET /portfolio returns portfolio summary."""
        resp = client_with_position.get("/api/v1/portfolio")
        assert resp.status_code == 200
        body = resp.json()
        assert "cash_balance" in body
        assert "drawdown_pct" in body
        assert "unrealised_pnl" in body

    def test_list_positions_with_data(self, client_with_position):
        """GET /portfolio/positions returns list of positions."""
        resp = client_with_position.get("/api/v1/portfolio/positions")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["symbol"] == "BTCUSDT"

    def test_list_positions_empty(self, client_empty):
        """GET /portfolio/positions returns empty list when flat."""
        resp = client_empty.get("/api/v1/portfolio/positions")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_position_found(self, client_with_position):
        """GET /portfolio/positions/{symbol} returns the position."""
        resp = client_with_position.get("/api/v1/portfolio/positions/BTCUSDT")
        assert resp.status_code == 200
        body = resp.json()
        assert body["symbol"] == "BTCUSDT"
        assert body["side"] == "BUY"

    def test_get_position_not_found(self, client_empty):
        """GET /portfolio/positions/{symbol} returns 404 when flat."""
        resp = client_empty.get("/api/v1/portfolio/positions/ETHUSDT")
        assert resp.status_code == 404
        assert resp.json()["detail"]["error"] == "position_not_found"

    def test_get_position_symbol_uppercased(self, client_with_position):
        """Symbol lookup should be case-insensitive (uppercased internally)."""
        resp = client_with_position.get("/api/v1/portfolio/positions/btcusdt")
        assert resp.status_code == 200
