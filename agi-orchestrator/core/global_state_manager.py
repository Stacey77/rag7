"""Global State Manager – system-wide async state store with pub/sub.

All sub-systems read and write state through this single object, which
guarantees thread/task-safe access via :class:`asyncio.Lock` and notifies
subscribers whenever a key changes.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")

# Type alias for async subscriber callbacks.
SubscriberCallback = Callable[[str, Any], Coroutine[Any, Any, None]]


class GlobalStateManager:
    """Thread-safe, async state store with subscriber notifications.

    Attributes:
        _state: Internal key-value store.
        _lock: Asyncio lock protecting concurrent state mutations.
        _subscribers: Mapping from state key to list of async callbacks.
    """

    def __init__(self) -> None:
        """Initialise an empty state store with no subscribers."""
        self._state: dict[str, Any] = {}
        self._lock: asyncio.Lock = asyncio.Lock()
        self._subscribers: defaultdict[str, list[SubscriberCallback]] = defaultdict(list)
        log.info("GlobalStateManager initialised")

    async def get_state(self, key: str, default: Any = None) -> Any:
        """Retrieve the current value for *key*.

        Args:
            key: State key to look up.
            default: Value returned when *key* is absent.

        Returns:
            The stored value, or *default* if the key does not exist.
        """
        async with self._lock:
            value = self._state.get(key, default)
        log.debug("State read", key=key, found=(key in self._state))
        return value

    async def update_state(self, key: str, value: Any) -> None:
        """Write *value* under *key* and notify all subscribers.

        Args:
            key: State key to update.
            value: New value to store.
        """
        async with self._lock:
            self._state[key] = value
        log.debug("State updated", key=key)
        await self._notify_subscribers(key, value)

    async def _notify_subscribers(self, key: str, value: Any) -> None:
        """Invoke all callbacks registered for *key*.

        Errors in individual callbacks are caught and logged so that a single
        misbehaving subscriber cannot block the notification chain.

        Args:
            key: The state key that changed.
            value: The new value.
        """
        callbacks = self._subscribers.get(key, [])
        for cb in callbacks:
            try:
                await cb(key, value)
            except Exception as exc:  # noqa: BLE001
                log.error("Subscriber callback failed", key=key, error=str(exc))

    def subscribe(self, key: str, callback: SubscriberCallback) -> None:
        """Register an async callback to be called whenever *key* changes.

        Args:
            key: State key to watch.
            callback: Async callable with signature
                ``async def cb(key: str, value: Any) -> None``.

        Raises:
            TypeError: If *callback* is not callable.
        """
        if not callable(callback):
            raise TypeError(f"callback must be callable, got {type(callback).__name__}")
        self._subscribers[key].append(callback)
        log.debug("Subscriber registered", key=key)

    async def get_all_state(self) -> dict[str, Any]:
        """Return a shallow copy of the entire state snapshot.

        Returns:
            Dictionary mapping every stored key to its current value.
        """
        async with self._lock:
            return dict(self._state)
