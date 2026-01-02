from __future__ import annotations

from typing import Final

ColorInput = str | tuple[int, int, int] | tuple[int, int, int, int]

_NAMED_COLORS: Final[dict[str, tuple[int, int, int]]] = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}


def parse_color(color: ColorInput) -> tuple[int, int, int]:
    if isinstance(color, tuple):
        if len(color) < 3:
            raise ValueError("Color tuple must be at least 3 integers")
        return _clamp_rgb(color[0], color[1], color[2])
    if not isinstance(color, str):
        raise TypeError("Color must be a string or RGB tuple")

    color = color.strip().lower()
    if color in _NAMED_COLORS:
        return _NAMED_COLORS[color]
    if color.startswith("#"):
        return _parse_hex(color[1:])
    if color.startswith("rgb(") and color.endswith(")"):
        parts = color[4:-1].split(",")
        if len(parts) != 3:
            raise ValueError("RGB color requires 3 components")
        return _clamp_rgb(*(int(p.strip()) for p in parts))

    raise ValueError(f"Unsupported color format: {color}")


def _parse_hex(value: str) -> tuple[int, int, int]:
    if len(value) == 3:
        r = int(value[0] * 2, 16)
        g = int(value[1] * 2, 16)
        b = int(value[2] * 2, 16)
        return _clamp_rgb(r, g, b)
    if len(value) == 6:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
        return _clamp_rgb(r, g, b)
    raise ValueError("Hex color must be 3 or 6 characters long")


def _clamp_rgb(red: int, green: int, blue: int) -> tuple[int, int, int]:
    return (
        _clamp_channel(red),
        _clamp_channel(green),
        _clamp_channel(blue),
    )


def _clamp_channel(value: int) -> int:
    return max(0, min(255, value))
