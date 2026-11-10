"""Common utilities for the trading platform.

Provides:

* :func:`retry` – async/sync exponential-backoff retry decorator.
* :class:`RateLimiter` – token-bucket async rate limiter.
* :class:`Timer` – context-manager and decorator stopwatch.
* Timestamp helpers: :func:`utc_now`, :func:`to_unix_ms`, :func:`from_unix_ms`.
* Dict helpers: :func:`deep_merge`, :func:`flatten_dict`, :func:`safe_get`.
"""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable, Coroutine
from datetime import datetime, timezone
from typing import Any, TypeVar, overload

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Retry decorator
# ---------------------------------------------------------------------------


def retry(
    *,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[F], F]:
    """Decorator that retries a sync or async callable on failure.

    Uses exponential back-off between attempts.

    Args:
        attempts: Maximum number of total call attempts (including the first).
        delay: Initial delay in seconds before the first retry.
        backoff: Multiplicative factor applied to *delay* after each failure.
        exceptions: Tuple of exception types that trigger a retry.
        on_retry: Optional callback invoked with ``(attempt, exception)``
            before each retry sleep.

    Returns:
        A decorator that wraps sync or async functions.

    Example::

        @retry(attempts=5, delay=0.5, exceptions=(IOError,))
        async def fetch_price(symbol: str) -> float:
            ...
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                current_delay = delay
                last_exc: Exception | None = None
                for attempt in range(1, attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as exc:
                        last_exc = exc
                        if attempt == attempts:
                            break
                        if on_retry:
                            on_retry(attempt, exc)
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                raise last_exc  # type: ignore[misc]

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exc: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == attempts:
                        break
                    if on_retry:
                        on_retry(attempt, exc)
                    time.sleep(current_delay)
                    current_delay *= backoff
            raise last_exc  # type: ignore[misc]

        return sync_wrapper  # type: ignore[return-value]

    return decorator  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class RateLimiter:
    """Async token-bucket rate limiter.

    Acquires one token per call, blocking until a token is available.

    Args:
        rate: Tokens replenished per second.
        capacity: Maximum burst capacity (defaults to *rate*).

    Example::

        limiter = RateLimiter(rate=10)
        async def fetch():
            await limiter.acquire()
            ...
    """

    def __init__(self, rate: float, capacity: float | None = None) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        self._rate = rate
        self._capacity = capacity if capacity is not None else rate
        self._tokens: float = self._capacity
        self._last_refill: float = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        """Add tokens proportional to elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            self._capacity, self._tokens + elapsed * self._rate
        )
        self._last_refill = now

    async def acquire(self, tokens: float = 1.0) -> None:
        """Wait until *tokens* are available, then consume them.

        Args:
            tokens: Number of tokens to consume (default 1).

        Raises:
            ValueError: If *tokens* exceeds bucket capacity.
        """
        if tokens > self._capacity:
            raise ValueError(
                f"Requested {tokens} tokens exceeds capacity {self._capacity}"
            )
        async with self._lock:
            while True:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                wait = (tokens - self._tokens) / self._rate
                await asyncio.sleep(wait)


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------


class Timer:
    """Context-manager and decorator stopwatch.

    Args:
        name: Optional label included in the string representation.

    Example::

        with Timer("order-routing") as t:
            await route_order(order)
        print(t.elapsed_ms)  # 42.1

        @Timer("inference")
        async def run_model(data):
            ...
    """

    def __init__(self, name: str = "") -> None:
        self.name = name
        self._start: float = 0.0
        self._end: float = 0.0

    # --- Context-manager protocol ---

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        self._end = time.perf_counter()

    # --- Async context-manager protocol ---

    async def __aenter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    async def __aexit__(self, *_: Any) -> None:
        self._end = time.perf_counter()

    # --- Decorator protocol ---

    @overload
    def __call__(self, func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]: ...

    @overload
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]: ...

    def __call__(self, func: Any) -> Any:  # noqa: D102
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                async with self:
                    return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with self:
                return func(*args, **kwargs)

        return sync_wrapper

    # --- Properties ---

    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds."""
        end = self._end or time.perf_counter()
        return end - self._start

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds."""
        return self.elapsed * 1_000.0

    def __str__(self) -> str:  # noqa: D105
        label = f"[{self.name}] " if self.name else ""
        return f"{label}{self.elapsed_ms:.3f} ms"

    def __repr__(self) -> str:  # noqa: D105
        return f"Timer(name={self.name!r}, elapsed_ms={self.elapsed_ms:.3f})"


# ---------------------------------------------------------------------------
# Timestamp helpers
# ---------------------------------------------------------------------------


def utc_now() -> datetime:
    """Return the current UTC datetime with timezone info.

    Returns:
        Timezone-aware :class:`datetime` in UTC.
    """
    return datetime.now(tz=timezone.utc)


def to_unix_ms(dt: datetime) -> int:
    """Convert a :class:`datetime` to a Unix timestamp in milliseconds.

    Args:
        dt: A timezone-aware or naive datetime (naive treated as UTC).

    Returns:
        Integer milliseconds since the Unix epoch.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000)


def from_unix_ms(ts_ms: int) -> datetime:
    """Convert a Unix millisecond timestamp to a UTC :class:`datetime`.

    Args:
        ts_ms: Milliseconds since the Unix epoch.

    Returns:
        Timezone-aware :class:`datetime` in UTC.
    """
    return datetime.fromtimestamp(ts_ms / 1_000.0, tz=timezone.utc)


# ---------------------------------------------------------------------------
# Dict utilities
# ---------------------------------------------------------------------------


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *override* into a copy of *base*.

    Nested dicts are merged recursively; all other types in *override* win.

    Args:
        base: The base dictionary.
        override: Values that overwrite *base*.

    Returns:
        New merged dictionary (neither input is mutated).
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def flatten_dict(
    nested: dict[str, Any],
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """Flatten a nested dictionary using dot-separated keys.

    Args:
        nested: The nested dictionary to flatten.
        parent_key: Prefix accumulated during recursion.
        sep: Key separator string.

    Returns:
        Flat dictionary with compound keys.

    Example::

        flatten_dict({"a": {"b": 1}})  # {"a.b": 1}
    """
    items: list[tuple[str, Any]] = []
    for k, v in nested.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely traverse a nested dict with a sequence of keys.

    Args:
        data: The dictionary to traverse.
        *keys: Ordered sequence of keys forming the path.
        default: Value returned when any key is absent.

    Returns:
        The nested value, or *default*.

    Example::

        safe_get(cfg, "exchange", "api_key", default="")
    """
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is default:
            return default
    return current
