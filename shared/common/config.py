"""Centralised application configuration via pydantic-settings.

Environment variables override YAML values using the prefix ``TRADING_``.
Examples::

    TRADING_DB_HOST=prod-db.internal
    TRADING_RISK_MAX_POSITION_SIZE_USD=250000
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL / TimescaleDB connection settings."""

    host: str = "localhost"
    port: int = 5432
    name: str = "trading"
    user: str = "trading_user"
    password: str = "changeme"
    pool_size: int = 10
    pool_max_overflow: int = 20

    model_config = SettingsConfigDict(env_prefix="TRADING_DB_")

    @property
    def dsn(self) -> str:
        """asyncpg-compatible DSN."""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50

    model_config = SettingsConfigDict(env_prefix="TRADING_REDIS_")

    @property
    def url(self) -> str:
        """redis-py compatible URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class ExchangeSettings(BaseSettings):
    """Exchange connectivity settings."""

    name: str = "alpaca"
    testnet: bool = True
    rest_base_url: str = "https://paper-api.alpaca.markets"
    ws_base_url: str = "wss://stream.data.alpaca.markets/v2"
    rate_limit_rps: int = 10

    model_config = SettingsConfigDict(env_prefix="TRADING_EXCHANGE_")


class RiskSettings(BaseSettings):
    """Pre-trade risk limit settings."""

    max_position_size_usd: float = 100_000.0
    max_portfolio_drawdown_pct: float = 10.0
    max_order_size_usd: float = 50_000.0
    daily_loss_limit_usd: float = 20_000.0

    model_config = SettingsConfigDict(env_prefix="TRADING_RISK_")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = "INFO"
    log_dir: str = "./logs"
    rotation: str = "100 MB"
    retention: str = "30 days"
    serialize: bool = False

    model_config = SettingsConfigDict(env_prefix="TRADING_LOG_")


class AGISettings(BaseSettings):
    """AGI orchestrator settings."""

    enabled: bool = True
    model_endpoint: str = "http://localhost:8080"
    timeout_seconds: float = 5.0
    confidence_threshold: float = 0.7

    model_config = SettingsConfigDict(env_prefix="TRADING_AGI_")


class AppConfig(BaseSettings):
    """Root application configuration."""

    environment: str = "development"
    service_name: str = "agi-trading-platform"
    debug: bool = False

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    exchange: ExchangeSettings = Field(default_factory=ExchangeSettings)
    risk: RiskSettings = Field(default_factory=RiskSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    agi: AGISettings = Field(default_factory=AGISettings)

    model_config = SettingsConfigDict(env_prefix="TRADING_")


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return the singleton application configuration."""
    return AppConfig()
