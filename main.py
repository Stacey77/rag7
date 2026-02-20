"""FastAPI application entry point for the AGI Trading Platform."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from shared.common.config import get_config
from shared.common.logger import configure_logger, get_logger

log = get_logger(__name__, service="main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown handlers."""
    cfg = get_config()
    configure_logger(
        log_level=cfg.logging.level,
        log_dir=cfg.logging.log_dir,
        serialize=cfg.logging.serialize,
    )
    log.info("AGI Trading Platform starting up", environment=cfg.environment)

    # TODO: Initialize exchange connectors, portfolio manager, data collectors
    # These will be wired up once the service layer is complete

    yield

    log.info("AGI Trading Platform shutting down")


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


@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """Platform health check endpoint."""
    return {"status": "healthy", "service": "agi-trading-platform", "version": "0.1.0"}


@app.get("/", tags=["system"])
async def root() -> dict:
    """Root endpoint with platform information."""
    return {
        "service": "AGI Trading Platform",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }
