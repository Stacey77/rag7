"""Pytest fixtures shared across all test modules."""

from __future__ import annotations

import asyncio
from decimal import Decimal

import pytest

from shared.models.ai_models import RiskAssessment
from shared.models.trading_models import Order, OrderType, OrderStatus, Position, Portfolio, Side


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_order() -> Order:
    """A sample market buy order for BTCUSDT."""
    return Order(
        symbol="BTCUSDT",
        side=Side.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.01"),
    )


@pytest.fixture
def sample_limit_order() -> Order:
    """A sample limit sell order for BTCUSDT."""
    return Order(
        symbol="BTCUSDT",
        side=Side.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.01"),
        price=Decimal("50000"),
    )


@pytest.fixture
def sample_position() -> Position:
    """A sample open long position in BTCUSDT."""
    return Position(
        symbol="BTCUSDT",
        side=Side.BUY,
        quantity=Decimal("0.5"),
        average_entry_price=Decimal("45000"),
    )


@pytest.fixture
def sample_portfolio(sample_position: Position) -> Portfolio:
    """A sample portfolio with one open position."""
    return Portfolio(
        account_id="test-account-001",
        positions={"BTCUSDT": sample_position},
        cash_balance=Decimal("50000"),
        total_equity=Decimal("72500"),
        peak_equity=Decimal("75000"),
    )


@pytest.fixture
def approved_risk_assessment() -> RiskAssessment:
    """An approved risk assessment fixture."""
    return RiskAssessment(
        symbol="BTCUSDT",
        proposed_quantity=Decimal("0.01"),
        proposed_notional_usd=Decimal("450"),
        current_drawdown_pct=3.33,
        is_approved=True,
        risk_score=0.2,
    )
