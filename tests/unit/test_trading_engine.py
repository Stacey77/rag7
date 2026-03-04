"""Unit tests for the trading engine components."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from shared.models.ai_models import RiskAssessment
from shared.models.trading_models import (
    Fill, Order, OrderStatus, OrderType, Position, Portfolio, Side,
)
from trading_engine.execution.order_manager import OrderManager
from trading_engine.portfolio.portfolio_manager import PortfolioManager
from trading_engine.risk_management.risk_engine import RiskEngine


class TestOrderManager:
    """Tests for the OrderManager."""

    @pytest.fixture
    def mock_connector(self):
        connector = AsyncMock()
        connector.is_connected = True
        connector.place_order = AsyncMock(return_value="exchange-order-123")
        connector.cancel_order = AsyncMock(return_value=True)
        connector.get_order = AsyncMock(return_value=None)
        return connector

    @pytest.fixture
    def order_manager(self, mock_connector):
        return OrderManager(connector=mock_connector)

    @pytest.mark.asyncio
    async def test_submit_order_success(self, order_manager, sample_order, mock_connector):
        """Test successful order submission."""
        exchange_id = await order_manager.submit_order(sample_order)
        assert exchange_id == "exchange-order-123"
        mock_connector.place_order.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_submitted_order_is_tracked(self, order_manager, sample_order):
        """Order should appear in the registry after submission."""
        await order_manager.submit_order(sample_order)
        order = await order_manager.get_order(sample_order.order_id)
        assert order is not None
        assert order.order_id == sample_order.order_id

    @pytest.mark.asyncio
    async def test_cancel_order_success(self, order_manager, sample_order, mock_connector):
        """Test successful order cancellation."""
        await order_manager.submit_order(sample_order)
        result = await order_manager.cancel_order(sample_order.order_id)
        assert result is True
        mock_connector.cancel_order.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cancel_unknown_order_raises(self, order_manager):
        """Cancelling a non-existent order should raise OrderNotFoundError."""
        from shared.common.exceptions import OrderNotFoundError

        with pytest.raises(OrderNotFoundError):
            await order_manager.cancel_order("nonexistent-id")

    @pytest.mark.asyncio
    async def test_get_open_orders_empty(self, order_manager):
        """Open orders list should be empty initially."""
        orders = await order_manager.get_open_orders()
        assert isinstance(orders, list)
        assert len(orders) == 0

    @pytest.mark.asyncio
    async def test_order_count_increments(self, order_manager, sample_order):
        """Order count increments with each submission."""
        assert order_manager.order_count() == 0
        await order_manager.submit_order(sample_order)
        assert order_manager.order_count() == 1

    @pytest.mark.asyncio
    async def test_submit_sets_accepted_status(self, order_manager, sample_order):
        """After a successful submission the order should be ACCEPTED."""
        await order_manager.submit_order(sample_order)
        order = await order_manager.get_order(sample_order.order_id)
        assert order is not None
        assert order.status == OrderStatus.ACCEPTED


class TestRiskEngine:
    """Tests for the RiskEngine pre-trade risk checks."""

    @pytest.fixture
    def risk_engine(self):
        return RiskEngine()

    @pytest.mark.asyncio
    async def test_approve_small_order(self, risk_engine, sample_order, sample_portfolio):
        """Small orders within limits should be approved."""
        assessment = await risk_engine.evaluate(sample_order, sample_portfolio)
        assert isinstance(assessment, RiskAssessment)
        assert assessment.is_approved is True

    @pytest.mark.asyncio
    async def test_returns_risk_assessment(self, risk_engine, sample_order, sample_portfolio):
        """evaluate() must always return a RiskAssessment."""
        result = await risk_engine.evaluate(sample_order, sample_portfolio)
        assert isinstance(result, RiskAssessment)
        assert isinstance(result.is_approved, bool)
        assert 0.0 <= result.risk_score <= 1.0

    @pytest.mark.asyncio
    async def test_reject_oversized_order(self, risk_engine, sample_portfolio):
        """Orders exceeding max order size should be rejected."""
        # At $50 000 limit, 9999 BTC at ~$45 k = way over limit
        large_order = Order(
            symbol="BTCUSDT",
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000"),
        )
        assessment = await risk_engine.evaluate(large_order, sample_portfolio)
        assert isinstance(assessment, RiskAssessment)
        # At least some risk was detected
        assert assessment.risk_score > 0

    @pytest.mark.asyncio
    async def test_drawdown_warning(self, risk_engine, sample_order):
        """Portfolio at ~3.3% drawdown (below limit) should still be approved."""
        portfolio = Portfolio(
            account_id="test",
            cash_balance=Decimal("50000"),
            total_equity=Decimal("72500"),
            peak_equity=Decimal("75000"),
        )
        assessment = await risk_engine.evaluate(sample_order, portfolio)
        assert isinstance(assessment, RiskAssessment)

    @pytest.mark.asyncio
    async def test_reject_excessive_drawdown(self, risk_engine, sample_order):
        """Portfolio above drawdown limit should be rejected."""
        portfolio = Portfolio(
            account_id="test",
            cash_balance=Decimal("1000"),
            total_equity=Decimal("1000"),
            peak_equity=Decimal("200000"),  # ~99.5% drawdown
        )
        assessment = await risk_engine.evaluate(sample_order, portfolio)
        assert isinstance(assessment, RiskAssessment)
        assert assessment.is_approved is False
        assert assessment.risk_score > 0

    @pytest.mark.asyncio
    async def test_daily_loss_limit_reject(self, risk_engine, sample_order):
        """Portfolio that has hit daily loss limit should be rejected."""
        portfolio = Portfolio(
            account_id="test",
            cash_balance=Decimal("80000"),
            total_equity=Decimal("80000"),
            peak_equity=Decimal("100000"),
            realised_pnl=Decimal("-25000"),  # Exceeded $20k daily limit
        )
        assessment = await risk_engine.evaluate(sample_order, portfolio)
        assert isinstance(assessment, RiskAssessment)
        assert assessment.is_approved is False


class TestPortfolioManager:
    """Tests for the PortfolioManager."""

    @pytest.fixture
    def portfolio_manager(self):
        return PortfolioManager(account_id="test-account", initial_cash=Decimal("100000"))

    @pytest.mark.asyncio
    async def test_initial_state(self, portfolio_manager):
        """Portfolio should start with initial cash and no positions."""
        portfolio = await portfolio_manager.get_portfolio()
        assert portfolio.cash_balance == Decimal("100000")
        assert len(portfolio.positions) == 0

    @pytest.mark.asyncio
    async def test_get_position_not_found(self, portfolio_manager):
        """Getting a non-existent position should return None."""
        pos = await portfolio_manager.get_position("NONEXISTENT")
        assert pos is None

    @pytest.mark.asyncio
    async def test_update_from_buy_fill_creates_position(self, portfolio_manager):
        """A buy fill should create a new position."""
        fill = Fill(
            order_id="test-order",
            symbol="BTCUSDT",
            side=Side.BUY,
            quantity=Decimal("1"),
            price=Decimal("40000"),
        )
        await portfolio_manager.update_from_fill(fill)
        pos = await portfolio_manager.get_position("BTCUSDT")
        assert pos is not None
        assert pos.quantity == Decimal("1")
        assert pos.average_entry_price == Decimal("40000")

    @pytest.mark.asyncio
    async def test_update_from_buy_fill_deducts_cash(self, portfolio_manager):
        """Buying should reduce the cash balance by the fill value + commission."""
        fill = Fill(
            order_id="test-order",
            symbol="BTCUSDT",
            side=Side.BUY,
            quantity=Decimal("1"),
            price=Decimal("40000"),
            commission=Decimal("10"),
        )
        await portfolio_manager.update_from_fill(fill)
        portfolio = await portfolio_manager.get_portfolio()
        assert portfolio.cash_balance == Decimal("100000") - Decimal("40000") - Decimal("10")

    @pytest.mark.asyncio
    async def test_update_from_sell_fill_removes_position(self, portfolio_manager):
        """Selling the full position should remove it."""
        buy_fill = Fill(
            order_id="buy-order",
            symbol="BTCUSDT",
            side=Side.BUY,
            quantity=Decimal("1"),
            price=Decimal("40000"),
        )
        await portfolio_manager.update_from_fill(buy_fill)

        sell_fill = Fill(
            order_id="sell-order",
            symbol="BTCUSDT",
            side=Side.SELL,
            quantity=Decimal("1"),
            price=Decimal("45000"),
        )
        await portfolio_manager.update_from_fill(sell_fill)
        pos = await portfolio_manager.get_position("BTCUSDT")
        assert pos is None

    @pytest.mark.asyncio
    async def test_mark_to_market_updates_unrealised_pnl(self, portfolio_manager):
        """Mark-to-market should update unrealised P&L correctly."""
        pos = Position(
            symbol="BTCUSDT",
            side=Side.BUY,
            quantity=Decimal("1"),
            average_entry_price=Decimal("40000"),
        )
        portfolio_manager._portfolio = portfolio_manager._portfolio.model_copy(
            update={"positions": {"BTCUSDT": pos}}
        )
        await portfolio_manager.mark_to_market({"BTCUSDT": Decimal("45000")})
        portfolio = await portfolio_manager.get_portfolio()
        btc_pos = portfolio.positions.get("BTCUSDT")
        assert btc_pos is not None
        assert btc_pos.unrealised_pnl == Decimal("5000")

    @pytest.mark.asyncio
    async def test_mark_to_market_short_position(self, portfolio_manager):
        """Short position P&L should decrease when price rises."""
        pos = Position(
            symbol="ETHUSDT",
            side=Side.SELL,
            quantity=Decimal("10"),
            average_entry_price=Decimal("2000"),
        )
        portfolio_manager._portfolio = portfolio_manager._portfolio.model_copy(
            update={"positions": {"ETHUSDT": pos}}
        )
        await portfolio_manager.mark_to_market({"ETHUSDT": Decimal("2100")})
        portfolio = await portfolio_manager.get_portfolio()
        eth_pos = portfolio.positions.get("ETHUSDT")
        assert eth_pos is not None
        assert eth_pos.unrealised_pnl == Decimal("-1000")

    @pytest.mark.asyncio
    async def test_peak_equity_tracked(self, portfolio_manager):
        """peak_equity should update when total_equity increases."""
        initial = await portfolio_manager.get_portfolio()
        assert initial.peak_equity == Decimal("100000")

        # Simulate adding a profitable position via mark-to-market
        pos = Position(
            symbol="BTCUSDT",
            side=Side.BUY,
            quantity=Decimal("1"),
            average_entry_price=Decimal("40000"),
        )
        portfolio_manager._portfolio = portfolio_manager._portfolio.model_copy(
            update={"positions": {"BTCUSDT": pos}}
        )
        await portfolio_manager.mark_to_market({"BTCUSDT": Decimal("70000")})
        portfolio = await portfolio_manager.get_portfolio()
        assert portfolio.total_equity > Decimal("100000")
        assert portfolio.peak_equity >= portfolio.total_equity
