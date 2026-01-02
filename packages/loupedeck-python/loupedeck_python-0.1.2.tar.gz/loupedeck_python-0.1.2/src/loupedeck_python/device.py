from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, overload

from .color import ColorInput, parse_color
from .constants import BUTTONS, COMMANDS, DEFAULT_RECONNECT_INTERVAL, HAPTIC, MAX_BRIGHTNESS
from .connections import LoupedeckSerialConnection, LoupedeckWebSocketConnection
from .events import AsyncEventEmitter
from .types import (
    ConnectionInfo,
    DeviceInfo,
    DisplayInfo,
    Touch,
    TouchEvent,
    TouchTarget,
)
from .util import rgb_to_rgb565


class LoupedeckDevice(AsyncEventEmitter):
    key_size: int = 90
    displays: dict[str, DisplayInfo]
    buttons: list[int | str]
    knobs: list[str]
    columns: int
    rows: int
    type: str
    visible_x: tuple[int, int]

    def __init__(
        self,
        *,
        host: str | None = None,
        path: str | None = None,
        auto_connect: bool = True,
        reconnect_interval: int | None = DEFAULT_RECONNECT_INTERVAL,
    ) -> None:
        super().__init__()
        self._transaction_id = 0
        self._touches: dict[int, Touch] = {}
        self._pending: dict[int, asyncio.Future[Any]] = {}
        self._reconnect_interval = reconnect_interval
        self._reconnect_task: asyncio.Task[None] | None = None
        self._connection: LoupedeckSerialConnection | LoupedeckWebSocketConnection | None = None
        self._host = host
        self._path = path
        self._handlers: dict[int, Callable[[bytes], Any]] = {
            COMMANDS["BUTTON_PRESS"]: self._on_button,
            COMMANDS["KNOB_ROTATE"]: self._on_rotate,
            COMMANDS["SERIAL"]: lambda payload: payload.decode().strip(),
            COMMANDS["TICK"]: lambda _payload: None,
            COMMANDS["TOUCH"]: lambda payload: self._on_touch("touchmove", payload),
            COMMANDS["TOUCH_END"]: lambda payload: self._on_touch("touchend", payload),
            COMMANDS["VERSION"]: lambda payload: f"{payload[0]}.{payload[1]}.{payload[2]}",
            COMMANDS["TOUCH_CT"]: lambda payload: self._on_touch("touchmove", payload),
            COMMANDS["TOUCH_END_CT"]: lambda payload: self._on_touch("touchend", payload),
        }
        if auto_connect:
            asyncio.create_task(self._connect_blind())

    @classmethod
    async def list(
        cls, *, ignore_serial: bool = False, ignore_websocket: bool = False
    ) -> list[ConnectionInfo]:
        tasks: list[Awaitable[list[ConnectionInfo]]] = []
        if not ignore_serial:
            tasks.append(LoupedeckSerialConnection.discover())
        if not ignore_websocket:
            tasks.append(LoupedeckWebSocketConnection.discover())
        if not tasks:
            return []
        results = await asyncio.gather(*tasks)
        devices: list[ConnectionInfo] = []
        for entries in results:
            devices.extend(entries)
        return devices

    async def connect(self) -> None:
        if self._path:
            self._connection = LoupedeckSerialConnection(self._path)
        elif self._host:
            self._connection = LoupedeckWebSocketConnection(self._host)
        else:
            devices = await self.list()
            if not devices:
                raise RuntimeError("No devices found")
            info = devices[0]
            if info.path:
                self._connection = LoupedeckSerialConnection(info.path)
            elif info.host:
                self._connection = LoupedeckWebSocketConnection(info.host)
            else:
                raise RuntimeError("Device connection information is incomplete")

        self._connection.on("connect", self._handle_connect)
        self._connection.on("message", self._handle_message)
        self._connection.on("disconnect", self._handle_disconnect)
        await self._connection.connect()

    async def close(self) -> None:
        if not self._connection:
            return
        await self._connection.close()
        self._connection = None

    async def draw_buffer(
        self,
        *,
        id: str,
        buffer: bytes,
        width: int | None = None,
        height: int | None = None,
        x: int = 0,
        y: int = 0,
        auto_refresh: bool = True,
    ) -> None:
        display_info = self._get_display_info(id)
        width = width or display_info.width
        height = height or display_info.height
        if display_info.offset:
            x += display_info.offset[0]
            y += display_info.offset[1]
        pixel_count = width * height * 2
        if len(buffer) != pixel_count:
            raise ValueError(f"Expected buffer length of {pixel_count}, got {len(buffer)}")
        header = bytearray(8)
        header[0:2] = x.to_bytes(2, "big")
        header[2:4] = y.to_bytes(2, "big")
        header[4:6] = width.to_bytes(2, "big")
        header[6:8] = height.to_bytes(2, "big")
        payload = display_info.id + bytes(header) + _swap_endianness(buffer, display_info.endianness)
        await self.send(COMMANDS["FRAMEBUFF"], payload)
        if auto_refresh:
            await self.refresh(id)

    async def draw_canvas(
        self,
        *,
        id: str,
        callback: Callable[[Any, int, int, Any], None],
        width: int | None = None,
        height: int | None = None,
        x: int = 0,
        y: int = 0,
        auto_refresh: bool = True,
    ) -> None:
        display_info = self._get_display_info(id)
        width = width or display_info.width
        height = height or display_info.height
        try:
            from PIL import Image, ImageDraw
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "draw_canvas requires Pillow. Install it with `uv add pillow`."
            ) from exc
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        callback(draw, width, height, image)
        rgb = image.tobytes()
        buffer = rgb_to_rgb565(rgb, width * height)
        await self.draw_buffer(
            id=id,
            buffer=buffer,
            width=width,
            height=height,
            x=x,
            y=y,
            auto_refresh=auto_refresh,
        )

    @overload
    async def draw_key(self, index: int, buffer: bytes) -> None:
        ...

    @overload
    async def draw_key(
        self, index: int, callback: Callable[[Any, int, int, Any], None]
    ) -> None:
        ...

    async def draw_key(
        self, index: int, buffer_or_callback: bytes | Callable[[Any, int, int, Any], None]
    ) -> None:
        if index < 0 or index >= self.columns * self.rows:
            raise ValueError(f"Key {index} is not a valid key")
        width = self.key_size
        height = self.key_size
        x = self.visible_x[0] + (index % self.columns) * width
        y = (index // self.columns) * height
        if isinstance(buffer_or_callback, (bytes, bytearray, memoryview)):
            await self.draw_buffer(
                id="center",
                buffer=bytes(buffer_or_callback),
                width=width,
                height=height,
                x=x,
                y=y,
            )
        else:
            await self.draw_canvas(
                id="center",
                callback=buffer_or_callback,
                width=width,
                height=height,
                x=x,
                y=y,
            )

    @overload
    async def draw_screen(self, id: str, buffer: bytes) -> None:
        ...

    @overload
    async def draw_screen(
        self, id: str, callback: Callable[[Any, int, int, Any], None]
    ) -> None:
        ...

    async def draw_screen(
        self, id: str, buffer_or_callback: bytes | Callable[[Any, int, int, Any], None]
    ) -> None:
        if isinstance(buffer_or_callback, (bytes, bytearray, memoryview)):
            await self.draw_buffer(id=id, buffer=bytes(buffer_or_callback))
        else:
            await self.draw_canvas(id=id, callback=buffer_or_callback)

    async def get_info(self) -> DeviceInfo:
        if not self._connection or not self._connection.is_ready():
            raise RuntimeError("Not connected")
        serial = await self.send(COMMANDS["SERIAL"])
        version = await self.send(COMMANDS["VERSION"])
        return {"serial": serial, "version": version}

    async def refresh(self, id: str) -> None:
        display_info = self._get_display_info(id)
        await self.send(COMMANDS["DRAW"], display_info.id)

    async def send(self, command: int, data: bytes = b"") -> Any:
        if not self._connection or not self._connection.is_ready():
            return None
        self._transaction_id = (self._transaction_id + 1) % 256
        if self._transaction_id == 0:
            self._transaction_id += 1
        length = min(3 + len(data), 0xFF)
        packet = bytes([length, command, self._transaction_id]) + data
        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        self._pending[self._transaction_id] = future
        self._connection.send(packet)
        return await future

    async def set_brightness(self, value: float) -> Any:
        byte = max(0, min(MAX_BRIGHTNESS, round(value * MAX_BRIGHTNESS)))
        return await self.send(COMMANDS["SET_BRIGHTNESS"], bytes([byte]))

    async def set_button_color(self, *, id: int | str, color: ColorInput) -> Any:
        key = next((k for k, v in BUTTONS.items() if v == id), None)
        if key is None:
            raise ValueError(f"Invalid button ID: {id}")
        red, green, blue = parse_color(color)
        return await self.send(
            COMMANDS["SET_COLOR"],
            bytes([key, red, green, blue]),
        )

    async def vibrate(self, pattern: int = HAPTIC["SHORT"]) -> Any:
        return await self.send(COMMANDS["SET_VIBRATION"], bytes([pattern]))

    def get_target(self, x: int, y: int, touch_id: int) -> TouchTarget:
        raise NotImplementedError

    async def _connect_blind(self) -> None:
        try:
            await self.connect()
        except Exception:
            return

    async def _handle_connect(self, payload: dict[str, Any]) -> None:
        await self.emit("connect", payload)

    async def _handle_disconnect(self, error: Exception | None) -> None:
        await self.emit("disconnect", error)
        if self._connection:
            self._connection = None
        if error and self._reconnect_interval:
            if self._reconnect_task and not self._reconnect_task.done():
                self._reconnect_task.cancel()
            self._reconnect_task = asyncio.create_task(self._reconnect_later())

    async def _reconnect_later(self) -> None:
        if not self._reconnect_interval:
            return
        await asyncio.sleep(self._reconnect_interval / 1000)
        await self._connect_blind()

    async def _handle_message(self, data: bytes) -> None:
        if len(data) < 3:
            return
        msg_length = data[0]
        command = data[1]
        transaction_id = data[2]
        payload = data[3:msg_length]
        handler = self._handlers.get(command)
        response = handler(payload) if handler else payload
        future = self._pending.pop(transaction_id, None)
        if future and not future.done():
            future.set_result(response)

    def _on_button(self, payload: bytes) -> None:
        if len(payload) < 2:
            return
        button_id = BUTTONS.get(payload[0], payload[0])
        event = "down" if payload[1] == 0x00 else "up"
        asyncio.create_task(self.emit(event, {"id": button_id}))

    def _on_rotate(self, payload: bytes) -> None:
        if len(payload) < 2:
            return
        knob_id = BUTTONS.get(payload[0], payload[0])
        delta = payload[1] if payload[1] < 128 else payload[1] - 256
        asyncio.create_task(self.emit("rotate", {"id": knob_id, "delta": delta}))

    def _on_touch(self, event: str, payload: bytes) -> None:
        if len(payload) < 6:
            return
        x = int.from_bytes(payload[1:3], "big")
        y = int.from_bytes(payload[3:5], "big")
        touch_id = payload[5]
        target = self.get_target(x, y, touch_id)
        touch = Touch(x=x, y=y, id=touch_id, target=target)
        if event == "touchend":
            self._touches.pop(touch_id, None)
        else:
            if touch_id not in self._touches:
                event = "touchstart"
            self._touches[touch_id] = touch
        payload_event: TouchEvent = {
            "touches": list(self._touches.values()),
            "changed_touches": [touch],
        }
        asyncio.create_task(self.emit(event, payload_event))

    def _get_display_info(self, display_id: str) -> DisplayInfo:
        display_info = self.displays.get(display_id)
        if not display_info:
            raise ValueError(f"Display '{display_id}' is not available on this device")
        return display_info


class LoupedeckLive(LoupedeckDevice):
    product_id = 0x0004
    vendor_id = 0x2EC2
    buttons = [0, 1, 2, 3, 4, 5, 6, 7]
    knobs = ["knobCL", "knobCR", "knobTL", "knobTR", "knobBL", "knobBR"]
    columns = 4
    displays = {
        "center": DisplayInfo(id=b"\x00M", width=360, height=270, offset=(60, 0)),
        "left": DisplayInfo(id=b"\x00M", width=60, height=270),
        "right": DisplayInfo(id=b"\x00M", width=60, height=270, offset=(420, 0)),
    }
    rows = 3
    type = "Loupedeck Live"
    visible_x = (0, 480)

    def get_target(self, x: int, y: int, touch_id: int) -> TouchTarget:
        if x < self.displays["left"].width:
            return {"screen": "left"}
        if x >= self.displays["left"].width + self.displays["center"].width:
            return {"screen": "right"}
        column = (x - self.displays["left"].width) // self.key_size
        row = y // self.key_size
        key = row * self.columns + column
        return {"screen": "center", "key": key}


class LoupedeckCT(LoupedeckLive):
    product_id = 0x0003
    buttons = [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        "home",
        "enter",
        "undo",
        "save",
        "keyboard",
        "fnL",
        "a",
        "b",
        "c",
        "d",
        "fnR",
        "e",
    ]
    displays = {
        "center": DisplayInfo(id=b"\x00A", width=360, height=270),
        "left": DisplayInfo(id=b"\x00L", width=60, height=270),
        "right": DisplayInfo(id=b"\x00R", width=60, height=270),
        "knob": DisplayInfo(id=b"\x00W", width=240, height=240, endianness="be"),
    }
    type = "Loupedeck CT"

    def get_target(self, x: int, y: int, touch_id: int) -> TouchTarget:
        if touch_id == 0:
            return {"screen": "knob"}
        return super().get_target(x, y, touch_id)


class LoupedeckLiveS(LoupedeckDevice):
    product_id = 0x0006
    vendor_id = 0x2EC2
    buttons = [0, 1, 2, 3]
    knobs = ["knobCL", "knobTL"]
    columns = 5
    displays = {
        "center": DisplayInfo(id=b"\x00M", width=480, height=270),
    }
    rows = 3
    type = "Loupedeck Live S"
    visible_x = (15, 465)

    def get_target(self, x: int, y: int, touch_id: int) -> TouchTarget:
        if x < self.visible_x[0] or x >= self.visible_x[1]:
            return {}
        column = (x - self.visible_x[0]) // self.key_size
        row = y // self.key_size
        key = row * self.columns + column
        return {"screen": "center", "key": key}


class RazerStreamController(LoupedeckLive):
    product_id = 0x0D06
    vendor_id = 0x1532
    type = "Razer Stream Controller"


class RazerStreamControllerX(LoupedeckDevice):
    product_id = 0x0D09
    vendor_id = 0x1532
    type = "Razer Stream Controller X"
    buttons: list[int | str] = []
    columns = 5
    displays = {
        "center": DisplayInfo(id=b"\x00M", width=480, height=288),
    }
    rows = 3
    visible_x = (0, 480)
    key_size = 96

    def get_target(self, x: int, y: int, touch_id: int) -> TouchTarget:
        column = x // self.key_size
        row = y // self.key_size
        key = row * self.columns + column
        return {"screen": "center", "key": key}

    def _on_button(self, payload: bytes) -> None:
        super()._on_button(payload)
        if len(payload) < 2:
            return
        event = "touchstart" if payload[1] == 0x00 else "touchend"
        key = BUTTONS.get(payload[0], payload[0])
        row = key // self.columns
        col = key % self.columns
        touch = Touch(
            id=0,
            x=int((col + 0.5) * self.key_size),
            y=int((row + 0.5) * self.key_size),
            target={"key": key},
        )
        payload_event: TouchEvent = {
            "touches": [touch] if event == "touchstart" else [],
            "changed_touches": [touch],
        }
        asyncio.create_task(self.emit(event, payload_event))

    async def set_button_color(self, *, id: int | str, color: ColorInput) -> Any:
        raise RuntimeError("Setting key color not available on this device")

    async def vibrate(self, pattern: int = HAPTIC["SHORT"]) -> Any:
        raise RuntimeError("Vibration not available on this device")


def _swap_endianness(buffer: bytes, endianness: str) -> bytes:
    if endianness != "be":
        return buffer
    swapped = bytearray(len(buffer))
    for i in range(0, len(buffer), 2):
        swapped[i] = buffer[i + 1]
        swapped[i + 1] = buffer[i]
    return bytes(swapped)
