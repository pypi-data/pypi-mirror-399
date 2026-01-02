from __future__ import annotations

import inspect
import logging
from typing import Any, Awaitable, Callable

EventHandler = Callable[[Any], Awaitable[None] | None]

logger = logging.getLogger(__name__)


class AsyncEventEmitter:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def off(self, event: str, handler: EventHandler) -> None:
        handlers = self._handlers.get(event)
        if not handlers:
            return
        try:
            handlers.remove(handler)
        except ValueError:
            return

    async def emit(self, event: str, payload: Any) -> None:
        for handler in list(self._handlers.get(event, [])):
            try:
                result = handler(payload)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                logger.exception("Unhandled error in '%s' event handler", event)
