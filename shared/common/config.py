"""Configuration management for the trading platform.

Loads settings from (in ascending priority order):

1. Hard-coded defaults
2. ``config.yaml`` found relative to the project root (or the path supplied
   via the ``CONFIG_FILE`` environment variable).
3. Environment variables with the prefix ``TRADING_``.

Uses *pydantic-settings* so every field is validated and type-coerced at
startup.  A singleton :func:`get_config` accessor avoids repeated parsing.

Example usage::

    from shared.common.config import get_config

    cfg = get_config()
    print(cfg.exchange.api_key)
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Sub-settings groups
# ---------------------------------------------------------------------------


class DatabaseSettings(BaseSettings):
    """Relational / time-series database connection settings."""

    model_config = SettingsConfigDict(env_prefix="TRADING_DB_", extra="ignore")

    host: str = Field("localhost", description="Database host.")
    port: int = Field(5432, ge=1, le=65535, description="Database port.")
    name: str = Field("trading", description="Database name.")
    user: str = Field("trading_user", description="Database user.")
    password: SecretStr = Field(
        SecretStr("changeme"), description="Database password."
    )
    pool_size: int = Field(10, ge=1, le=200, description="Connection pool size.")
    pool_max_overflow: int = Field(20, ge=0, description="Max pool overflow.")

    @property
    def dsn(self) -> str:
        """Return a PostgreSQL DSN string (password not redacted)."""
        pwd = self.password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.user}:{pwd}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class RedisSettings(BaseSettings):
    """Redis cache / pub-sub settings."""

    model_config = SettingsConfigDict(env_prefix="TRADING_REDIS_", extra="ignore")

    host: str = Field("localhost", description="Redis host.")
    port: int = Field(6379, ge=1, le=65535, description="Redis port.")
    db: int = Field(0, ge=0, le=15, description="Redis logical database index.")
    password: SecretStr | None = Field(None, description="Redis password.")
    max_connections: int = Field(50, ge=1, description="Connection pool size.")


class ExchangeSettings(BaseSettings):
    """Exchange connectivity settings."""

    model_config = SettingsConfigDict(env_prefix="TRADING_EXCHANGE_", extra="ignore")

    name: str = Field("binance", description="Exchange identifier slug.")
    api_key: SecretStr = Field(
        SecretStr(""), description="Exchange REST/WebSocket API key."
    )
    api_secret: SecretStr = Field(
        SecretStr(""), description="Exchange API secret."
    )
    testnet: bool = Field(True, description="Use the exchange sandbox/testnet.")
    rest_base_url: AnyHttpUrl = Field(
        "https://testnet.binance.vision",  # type: ignore[assignment]
        description="REST API base URL.",
    )
    ws_base_url: str = Field(
        "wss://testnet.binance.vision/ws",
        description="WebSocket base URL.",
    )
    rate_limit_rps: int = Field(
        10, ge=1, description="Requests per second allowed by the exchange."
    )


class RiskSettings(BaseSettings):
    """Risk-management parameters."""

    model_config = SettingsConfigDict(env_prefix="TRADING_RISK_", extra="ignore")

    max_position_size_usd: float = Field(
        100_000.0, gt=0, description="Maximum single-position value in USD."
    )
    max_portfolio_drawdown_pct: float = Field(
        10.0, gt=0, le=100, description="Hard drawdown limit as a percentage."
    )
    max_order_size_usd: float = Field(
        50_000.0, gt=0, description="Maximum single-order value in USD."
    )
    daily_loss_limit_usd: float = Field(
        20_000.0, gt=0, description="Maximum daily realised loss before halt."
    )


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(env_prefix="TRADING_LOG_", extra="ignore")

    level: str = Field("INFO", description="Log level.")
    log_dir: str | None = Field(None, description="Directory for rotating log files.")
    rotation: str = Field("100 MB", description="Log rotation trigger.")
    retention: str = Field("30 days", description="Log retention policy.")
    serialize: bool = Field(False, description="Emit JSON log lines.")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Ensure log level is a valid loguru level."""
        valid = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Invalid log level {v!r}. Must be one of {valid}.")
        return upper


class AGISettings(BaseSettings):
    """AGI orchestration settings."""

    model_config = SettingsConfigDict(env_prefix="TRADING_AGI_", extra="ignore")

    enabled: bool = Field(True, description="Enable AGI decision layer.")
    model_endpoint: str = Field(
        "http://localhost:8080", description="AGI model inference endpoint."
    )
    timeout_seconds: float = Field(5.0, gt=0, description="Inference timeout.")
    confidence_threshold: float = Field(
        0.7, ge=0.0, le=1.0, description="Minimum signal confidence to act."
    )


# ---------------------------------------------------------------------------
# Root settings
# ---------------------------------------------------------------------------


class TradingPlatformSettings(BaseSettings):
    """Root configuration for the trading platform.

    Environment variables are prefixed with ``TRADING_``.  Nested models read
    their own prefixes (e.g. ``TRADING_DB_HOST``).
    """

    model_config = SettingsConfigDict(
        env_prefix="TRADING_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    environment: str = Field(
        "development",
        description="Deployment environment (development | staging | production).",
    )
    service_name: str = Field("trading-platform", description="Service identifier.")
    debug: bool = Field(False, description="Enable debug mode.")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    exchange: ExchangeSettings = Field(default_factory=ExchangeSettings)
    risk: RiskSettings = Field(default_factory=RiskSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    agi: AGISettings = Field(default_factory=AGISettings)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Constrain to known deployment tiers."""
        valid = {"development", "staging", "production"}
        if v not in valid:
            raise ValueError(
                f"Unknown environment {v!r}. Must be one of {valid}."
            )
        return v

    @classmethod
    def from_yaml(cls, path: Path) -> "TradingPlatformSettings":
        """Build settings from a YAML file, then overlay environment variables.

        Args:
            path: Absolute or relative path to ``config.yaml``.

        Returns:
            A fully validated :class:`TradingPlatformSettings` instance.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If the YAML content fails validation.
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with path.open("r", encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}

        return cls(**raw)


def _resolve_config_path() -> Path | None:
    """Locate a config.yaml file using the CONFIG_FILE env var or defaults."""
    env_path = os.getenv("CONFIG_FILE")
    if env_path:
        return Path(env_path)

    # Walk up from cwd looking for config.yaml
    for candidate in (Path.cwd(), Path.cwd().parent, Path(__file__).parents[3]):
        p = candidate / "config.yaml"
        if p.exists():
            return p

    return None


@lru_cache(maxsize=1)
def get_config() -> TradingPlatformSettings:
    """Return the singleton platform configuration.

    Loads from YAML (if found) then overlays environment variables.  Cached
    after first call for the lifetime of the process.

    Returns:
        The validated :class:`TradingPlatformSettings` instance.
    """
    config_path = _resolve_config_path()
    if config_path:
        return TradingPlatformSettings.from_yaml(config_path)
    return TradingPlatformSettings()
