from __future__ import annotations


def rgba_to_rgb565(rgba: bytes, pixel_count: int) -> bytes:
    output = bytearray(pixel_count * 2)
    out_index = 0
    for i in range(0, pixel_count * 4, 4):
        red = rgba[i]
        green = rgba[i + 1]
        blue = rgba[i + 2]
        color = blue >> 3
        color |= (green & 0xFC) << 3
        color |= (red & 0xF8) << 8
        output[out_index] = color & 0xFF
        output[out_index + 1] = (color >> 8) & 0xFF
        out_index += 2
    return bytes(output)


def rgb_to_rgb565(rgb: bytes, pixel_count: int) -> bytes:
    output = bytearray(pixel_count * 2)
    out_index = 0
    for i in range(0, pixel_count * 3, 3):
        red = rgb[i]
        green = rgb[i + 1]
        blue = rgb[i + 2]
        color = blue >> 3
        color |= (green & 0xFC) << 3
        color |= (red & 0xF8) << 8
        output[out_index] = color & 0xFF
        output[out_index + 1] = (color >> 8) & 0xFF
        out_index += 2
    return bytes(output)
