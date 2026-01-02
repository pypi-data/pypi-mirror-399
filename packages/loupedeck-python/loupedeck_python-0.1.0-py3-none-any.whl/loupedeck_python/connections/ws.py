from __future__ import annotations

import asyncio
import time
from typing import Final

import psutil
import websockets

from ..constants import CONNECTION_TIMEOUT
from ..types import ConnectionInfo
from .base import BaseConnection


class LoupedeckWebSocketConnection(BaseConnection):
    def __init__(self, host: str) -> None:
        super().__init__()
        self._host = host
        self._address = f"ws://{host}"
        self._connection: websockets.WebSocketClientProtocol | None = None
        self._read_task: asyncio.Task[None] | None = None
        self._keepalive_task: asyncio.Task[None] | None = None
        self._last_tick = time.monotonic()
        self._connection_timeout = CONNECTION_TIMEOUT / 1000

    @classmethod
    async def discover(cls) -> list[ConnectionInfo]:
        results: list[ConnectionInfo] = []
        for addresses in psutil.net_if_addrs().values():
            for address in addresses:
                if not address.address.startswith("100.127"):
                    continue
                host = _replace_last_octet(address.address, "1")
                results.append(
                    ConnectionInfo(
                        connection_type=cls,
                        product_id=0x0004,
                        vendor_id=None,
                        host=host,
                    )
                )
        return results

    async def connect(self) -> None:
        self._connection = await websockets.connect(self._address)
        self._read_task = asyncio.create_task(self._read_loop())
        self._keepalive_task = asyncio.create_task(self._keepalive())
        await self.emit("connect", {"address": self._address})

    def is_ready(self) -> bool:
        return self._connection is not None and not self._connection.closed

    async def close(self) -> None:
        if not self._connection:
            return
        if self._read_task:
            self._read_task.cancel()
        if self._keepalive_task:
            self._keepalive_task.cancel()
        await self._connection.close()
        await self.emit("disconnect", None)

    def send(self, data: bytes, raw: bool = False) -> None:
        if raw:
            raise ValueError("WebSocket connection does not support raw frames")
        if not self._connection:
            return
        asyncio.create_task(self._connection.send(data))

    async def _read_loop(self) -> None:
        if not self._connection:
            return
        try:
            async for message in self._connection:
                if isinstance(message, bytes):
                    self._last_tick = time.monotonic()
                    await self.emit("message", message)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            await self.emit("disconnect", exc)
        else:
            await self.emit("disconnect", None)

    async def _keepalive(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._connection_timeout * 2)
                if time.monotonic() - self._last_tick > self._connection_timeout:
                    await self.emit("disconnect", RuntimeError("Connection timeout"))
                    await self.close()
                    return
        except asyncio.CancelledError:
            return


def _replace_last_octet(address: str, value: str) -> str:
    parts = address.split(".")
    if len(parts) != 4:
        return address
    parts[-1] = value
    return ".".join(parts)
