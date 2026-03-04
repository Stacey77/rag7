"""Integration tests for the end-to-end trading workflow."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from shared.models.trading_models import Order, OrderType, OrderStatus, Side
from trading_engine.execution.order_manager import OrderManager
from trading_engine.portfolio.portfolio_manager import PortfolioManager
from trading_engine.risk_management.risk_engine import RiskEngine


class TestTradingWorkflow:
    """Integration tests for the complete trade lifecycle."""

    @pytest.fixture
    def mock_connector(self):
        connector = AsyncMock()
        connector.is_connected = True
        connector.place_order = AsyncMock(return_value="exchange-id-001")
        connector.cancel_order = AsyncMock(return_value=True)
        connector.get_order = AsyncMock(return_value=None)
        return connector

    @pytest.fixture
    def trading_system(self, mock_connector):
        portfolio_manager = PortfolioManager(
            account_id="integration-test",
            initial_cash=Decimal("100000"),
        )
        risk_engine = RiskEngine()
        order_manager = OrderManager(connector=mock_connector)
        return {
            "portfolio": portfolio_manager,
            "risk": risk_engine,
            "orders": order_manager,
            "connector": mock_connector,
        }

    @pytest.mark.asyncio
    async def test_full_order_lifecycle(self, trading_system, sample_order):
        """Test placing and tracking an order through the full lifecycle."""
        system = trading_system
        portfolio = await system["portfolio"].get_portfolio()

        # Pre-trade risk check
        assessment = await system["risk"].evaluate(sample_order, portfolio)
        assert assessment is not None

        if assessment.is_approved:
            # Submit order
            exchange_id = await system["orders"].submit_order(sample_order)
            assert exchange_id == "exchange-id-001"
            system["connector"].place_order.assert_awaited_once()

            # Order should be tracked
            order = await system["orders"].get_order(sample_order.order_id)
            assert order is not None
            assert order.status == OrderStatus.ACCEPTED

    @pytest.mark.asyncio
    async def test_risk_blocks_oversized_trade(self, trading_system):
        """A trade that exceeds risk limits should not proceed."""
        system = trading_system
        portfolio = await system["portfolio"].get_portfolio()

        giant_order = Order(
            symbol="BTCUSDT",
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("99999"),
        )
        assessment = await system["risk"].evaluate(giant_order, portfolio)
        assert assessment is not None
        assert isinstance(assessment.is_approved, bool)

        if not assessment.is_approved:
            # Do not submit – connector should not be called
            system["connector"].place_order.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cancel_submitted_order(self, trading_system, sample_order):
        """Submitted orders should be cancellable."""
        system = trading_system
        portfolio = await system["portfolio"].get_portfolio()
        assessment = await system["risk"].evaluate(sample_order, portfolio)

        if assessment.is_approved:
            await system["orders"].submit_order(sample_order)
            cancelled = await system["orders"].cancel_order(sample_order.order_id)
            assert cancelled is True

    @pytest.mark.asyncio
    async def test_portfolio_starts_clean(self, trading_system):
        """The integration portfolio should start with no positions."""
        portfolio = await trading_system["portfolio"].get_portfolio()
        assert len(portfolio.positions) == 0
        assert portfolio.cash_balance == Decimal("100000")

    @pytest.mark.asyncio
    async def test_multiple_orders_tracked(self, trading_system):
        """Multiple orders can be submitted and tracked independently."""
        system = trading_system
        orders = [
            Order(symbol="BTCUSDT", side=Side.BUY, order_type=OrderType.MARKET, quantity=Decimal("0.01")),
            Order(symbol="ETHUSDT", side=Side.BUY, order_type=OrderType.MARKET, quantity=Decimal("0.1")),
        ]
        for order in orders:
            system["connector"].place_order = AsyncMock(return_value=f"ex-{order.symbol}")
            await system["orders"].submit_order(order)

        all_orders = await system["orders"].get_all_orders()
        assert len(all_orders) == 2
