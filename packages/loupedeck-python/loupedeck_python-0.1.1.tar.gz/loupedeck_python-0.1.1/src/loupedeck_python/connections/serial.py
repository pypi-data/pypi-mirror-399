from __future__ import annotations

import asyncio
import contextlib
from typing import Final

import serial_asyncio
from serial.tools import list_ports

from ..parser import MagicByteLengthParser
from ..types import ConnectionInfo
from .base import BaseConnection

WS_UPGRADE_HEADER: Final[bytes] = (
    b"GET /index.html\n"
    b"HTTP/1.1\n"
    b"Connection: Upgrade\n"
    b"Upgrade: websocket\n"
    b"Sec-WebSocket-Key: 123abc\n\n"
)
WS_UPGRADE_RESPONSE: Final[bytes] = b"HTTP/1.1"
WS_CLOSE_FRAME: Final[bytes] = bytes([0x88, 0x80, 0x00, 0x00, 0x00, 0x00])

VENDOR_IDS: Final[set[int]] = {0x2EC2, 0x1532}
MANUFACTURERS: Final[set[str]] = {"Loupedeck", "Razer"}


class LoupedeckSerialConnection(BaseConnection):
    def __init__(self, path: str) -> None:
        super().__init__()
        self._path = path
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._read_task: asyncio.Task[None] | None = None
        self._parser = MagicByteLengthParser(0x82)

    @classmethod
    async def discover(cls) -> list[ConnectionInfo]:
        results: list[ConnectionInfo] = []
        for info in list_ports.comports():
            vendor_id = info.vid
            product_id = info.pid
            manufacturer = info.manufacturer or ""
            if vendor_id is None and not manufacturer:
                continue
            if vendor_id not in VENDOR_IDS and manufacturer not in MANUFACTURERS:
                continue
            if product_id is None:
                continue
            results.append(
                ConnectionInfo(
                    connection_type=cls,
                    product_id=product_id,
                    vendor_id=vendor_id,
                    path=info.device,
                    serial_number=info.serial_number,
                )
            )
        return results

    async def connect(self) -> None:
        self._reader, self._writer = await serial_asyncio.open_serial_connection(
            url=self._path,
            baudrate=256000,
        )
        await self._perform_handshake()
        self._read_task = asyncio.create_task(self._read_loop())
        await self.emit("connect", {"address": self._path})

    def is_ready(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def close(self) -> None:
        if not self._writer:
            return
        self.send(WS_CLOSE_FRAME, raw=True)
        if self._read_task:
            self._read_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._read_task
        self._writer.close()
        await self._writer.wait_closed()
        await self.emit("disconnect", None)

    def send(self, data: bytes, raw: bool = False) -> None:
        if not self._writer:
            return
        if not raw:
            header = self._build_header(data)
            self._writer.write(header)
        self._writer.write(data)

    async def _perform_handshake(self) -> None:
        if not self._reader or not self._writer:
            raise RuntimeError("Serial connection is not initialized")
        self._writer.write(WS_UPGRADE_HEADER)
        response = await self._reader.read(64)
        if not response.startswith(WS_UPGRADE_RESPONSE):
            raise RuntimeError(f"Invalid handshake response: {response!r}")

    async def _read_loop(self) -> None:
        if not self._reader:
            return
        try:
            while True:
                data = await self._reader.read(1024)
                if not data:
                    break
                for message in self._parser.feed(data):
                    await self.emit("message", message)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            await self.emit("disconnect", exc)
        else:
            await self.emit("disconnect", None)

    @staticmethod
    def _build_header(data: bytes) -> bytes:
        length = len(data)
        if length > 0xFF:
            header = bytearray(14)
            header[0] = 0x82
            header[1] = 0xFF
            header[6:10] = length.to_bytes(4, "big")
            return bytes(header)
        header = bytearray(6)
        header[0] = 0x82
        header[1] = 0x80 + length
        return bytes(header)

