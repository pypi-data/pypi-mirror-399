from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict


@dataclass(frozen=True)
class DisplayInfo:
    id: bytes
    width: int
    height: int
    offset: tuple[int, int] | None = None
    endianness: Literal["le", "be"] = "le"


@dataclass(frozen=True)
class ConnectionInfo:
    connection_type: type["AsyncConnection"]
    product_id: int
    vendor_id: int | None
    path: str | None = None
    host: str | None = None
    serial_number: str | None = None


class TouchTarget(TypedDict, total=False):
    screen: str
    key: int


@dataclass
class Touch:
    x: int
    y: int
    id: int
    target: TouchTarget


class TouchEvent(TypedDict):
    touches: list[Touch]
    changed_touches: list[Touch]


class RotateEvent(TypedDict):
    id: int | str
    delta: int


class ButtonEvent(TypedDict):
    id: int | str


class ConnectEvent(TypedDict):
    address: str


class DeviceInfo(TypedDict):
    serial: str
    version: str


class AsyncConnection:
    async def connect(self) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError

    def is_ready(self) -> bool:
        raise NotImplementedError

    def send(self, data: bytes, raw: bool = False) -> None:
        raise NotImplementedError

    def on(self, event: str, handler: "EventHandler") -> None:
        raise NotImplementedError


from .events import EventHandler  # noqa: E402  (avoid circular import at runtime)
