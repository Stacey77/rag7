"""Structured logging configuration backed by loguru.

Usage::

    from shared.common.logger import configure_logger, get_logger

    configure_logger(log_level="DEBUG")
    log = get_logger(__name__, service="my-service")
    log.info("Something happened", key="value")
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def configure_logger(
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    rotation: str = "100 MB",
    retention: str = "30 days",
    serialize: bool = False,
) -> None:
    """Configure loguru with console and optional file sinks.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_dir: Directory for rotating log files. None disables file logging.
        rotation: loguru rotation policy (size or time string).
        retention: loguru retention policy.
        serialize: Emit JSON-structured log records when True.
    """
    logger.remove()  # Remove default handler

    # Console sink
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        colorize=not serialize,
        serialize=serialize,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        if not serialize
        else "{message}",
        backtrace=True,
        diagnose=True,
    )

    # File sink (optional)
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_path / "trading_{time}.log",
            level=log_level.upper(),
            rotation=rotation,
            retention=retention,
            serialize=serialize,
            compression="gz",
            enqueue=True,  # Thread-safe async logging
            backtrace=True,
            diagnose=True,
        )


def get_logger(name: str, **context: object) -> "logger":  # type: ignore[name-defined]
    """Return a loguru logger bound with the given context fields.

    Args:
        name: Module name (use ``__name__``).
        **context: Additional key/value pairs permanently bound to the logger.

    Returns:
        A loguru bound logger instance.
    """
    return logger.bind(module=name, **context)
