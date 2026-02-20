"""Centralized structured logging for the trading platform.

Provides a configured loguru logger with structured output, log rotation,
context binding, and environment-aware log levels.
"""

import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from loguru import logger as _logger

# Context variable for request/correlation ID propagation
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def _correlation_filter(record: dict[str, Any]) -> bool:
    """Inject correlation ID from context into every log record.

    Args:
        record: The loguru log record dict.

    Returns:
        Always True so the record is never filtered out.
    """
    record["extra"].setdefault("correlation_id", _correlation_id.get())
    return True


def configure_logger(
    log_level: str = "INFO",
    log_dir: str | None = None,
    rotation: str = "100 MB",
    retention: str = "30 days",
    compression: str = "gz",
    serialize: bool = False,
) -> None:
    """Configure the global loguru logger.

    Sets up a stderr sink and, optionally, a rotating file sink.  Both sinks
    use structured formatting and include the correlation ID from the current
    async/thread context.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_dir: Directory for log files.  When *None* no file sink is added.
        rotation: File-rotation policy accepted by loguru (e.g. ``"100 MB"``).
        retention: How long old log files are kept (e.g. ``"30 days"``).
        compression: Compression format for rotated files (``"gz"`` or ``"zip"``).
        serialize: When *True* each line is emitted as a JSON object.
    """
    _logger.remove()

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<yellow>{extra[correlation_id]}</yellow> - "
        "<level>{message}</level>"
    )

    _logger.add(
        sys.stderr,
        level=log_level,
        format=fmt,
        filter=_correlation_filter,
        colorize=True,
        backtrace=True,
        diagnose=True,
        serialize=serialize,
    )

    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        _logger.add(
            log_path / "trading_{time:YYYY-MM-DD}.log",
            level=log_level,
            format=fmt,
            filter=_correlation_filter,
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=True,
            diagnose=False,
            serialize=serialize,
            enqueue=True,  # thread-safe async logging
        )


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current execution context.

    Args:
        correlation_id: Unique identifier to attach to all subsequent log lines
            emitted from the current async task or thread.
    """
    _correlation_id.set(correlation_id)


def get_logger(name: str, **context: Any):
    """Return a context-bound logger for a specific module.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.
        **context: Arbitrary key-value pairs bound to every record from this
            logger instance (e.g. ``service="order-manager"``).

    Returns:
        A loguru logger with the supplied context pre-bound.

    Example::

        log = get_logger(__name__, service="risk-engine")
        log.info("position evaluated", symbol="BTCUSDT", pnl=1234.56)
    """
    return _logger.bind(module=name, **context)


# Apply default configuration so the module is usable without explicit setup.
configure_logger()

# Public re-export for convenience.
log = _logger
