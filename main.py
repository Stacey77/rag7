"""FastAPI application entry point for the AGI Trading Platform."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app

from shared.common.config import get_config
from shared.common.logger import configure_logger, get_logger
from trading_engine.api.router import router as trading_router
from trading_engine.execution.order_manager import OrderManager
from trading_engine.portfolio.portfolio_manager import PortfolioManager
from trading_engine.risk_management.risk_engine import RiskEngine

log = get_logger(__name__, service="main")

INITIAL_CASH_USD = Decimal("1_000_000")  # default paper-trading starting balance


def _build_connector():
    """Return a connector suited to the current environment.

    * If ``ALPACA_API_KEY`` is set, return a live :class:`AlpacaConnector`
      (paper mode when ``TRADING_EXCHANGE_TESTNET=true``, the default).
    * Otherwise fall back to the in-memory :class:`PaperConnector` so the
      app starts without any exchange credentials.
    """
    cfg = get_config()
    alpaca_key = os.getenv("ALPACA_API_KEY", "")
    if alpaca_key:
        from trading_engine.connectors.alpaca_connector import AlpacaConnector
        return AlpacaConnector(
            api_key=alpaca_key,
            secret_key=os.getenv("ALPACA_SECRET_KEY", ""),
            paper=cfg.exchange.testnet,
        )
    from trading_engine.connectors.paper_connector import PaperConnector
    log.info("No ALPACA_API_KEY found — using PaperConnector (simulation mode)")
    return PaperConnector()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: wire up and tear down service layer."""
    cfg = get_config()
    configure_logger(
        log_level=cfg.logging.level,
        log_dir=cfg.logging.log_dir,
        serialize=cfg.logging.serialize,
    )
    log.info("AGI Trading Platform starting up", environment=cfg.environment)

    # ── Build service instances ───────────────────────────────────────────
    connector = _build_connector()
    await connector.connect()

    app.state.connector = connector
    app.state.portfolio_manager = PortfolioManager(
        account_id=cfg.environment,
        initial_cash=INITIAL_CASH_USD,
    )
    app.state.risk_engine = RiskEngine(settings=cfg.risk)
    app.state.order_manager = OrderManager(connector=connector)

    log.info(
        "Service layer ready",
        connector=connector.exchange_name,
        paper=connector.is_paper_mode,
    )

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────
    await connector.disconnect()
    log.info("AGI Trading Platform shut down cleanly")


app = FastAPI(
    title="AGI Trading Platform",
    description=(
        "AI-powered algorithmic trading platform with AGI orchestration, "
        "multi-exchange connectivity, and real-time risk management."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Mount trading engine API
app.include_router(trading_router)


@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """Platform health check endpoint."""
    return {"status": "healthy", "service": "agi-trading-platform", "version": "0.1.0"}


_DASHBOARD_HTML = Path(__file__).parent / "index.html"


@app.get("/", tags=["system"], include_in_schema=False)
async def root() -> FileResponse:
    """Serve the trading platform HTML dashboard."""
    return FileResponse(_DASHBOARD_HTML, media_type="text/html")
