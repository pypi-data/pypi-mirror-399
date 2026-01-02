from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..events import AsyncEventEmitter
from ..types import ConnectionInfo


class BaseConnection(AsyncEventEmitter, ABC):
    @classmethod
    @abstractmethod
    async def discover(cls) -> list[ConnectionInfo]:
        raise NotImplementedError

    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def send(self, data: bytes, raw: bool = False) -> None:
        raise NotImplementedError

    async def on_event(self, event: str, payload: Any) -> None:
        await self.emit(event, payload)
