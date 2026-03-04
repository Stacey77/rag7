"""General-purpose utility helpers used across the platform."""

from __future__ import annotations

import asyncio
import hashlib
import time
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# ── Decimal helpers ────────────────────────────────────────────────────────


def round_decimal(value: Decimal, places: int = 8) -> Decimal:
    """Round a Decimal to *places* decimal places using ROUND_HALF_UP.

    Args:
        value: The value to round.
        places: Number of decimal places (default 8 for crypto precision).

    Returns:
        Rounded Decimal.
    """
    quantize_str = Decimal("0." + "0" * places)
    return value.quantize(quantize_str, rounding=ROUND_HALF_UP)


def to_decimal(value: Any) -> Decimal:
    """Safely convert a value to Decimal.

    Args:
        value: Any numeric type or string.

    Returns:
        Decimal representation.

    Raises:
        ValueError: If conversion fails.
    """
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"Cannot convert {value!r} to Decimal: {exc}") from exc


# ── Retry decorator ────────────────────────────────────────────────────────


def async_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Async retry decorator with exponential back-off.

    Args:
        max_attempts: Maximum number of total attempts.
        initial_delay: Delay (seconds) before the first retry.
        backoff_factor: Multiplier applied to the delay on each retry.
        exceptions: Tuple of exception types that trigger a retry.

    Returns:
        Decorated coroutine function.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
            raise RuntimeError(
                f"{func.__name__} failed after {max_attempts} attempts"
            ) from last_exc

        return wrapper  # type: ignore[return-value]

    return decorator


# ── Hashing ────────────────────────────────────────────────────────────────


def sha256_hex(data: str) -> str:
    """Return the SHA-256 hex digest of *data*."""
    return hashlib.sha256(data.encode()).hexdigest()


# ── Timing ────────────────────────────────────────────────────────────────


class Timer:
    """Context manager that measures elapsed wall-clock time in milliseconds.

    Usage::

        with Timer() as t:
            do_something()
        print(t.elapsed_ms)
    """

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1_000
