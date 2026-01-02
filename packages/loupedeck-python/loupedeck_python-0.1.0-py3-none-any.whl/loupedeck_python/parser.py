from __future__ import annotations


class MagicByteLengthParser:
    def __init__(self, magic_byte: int) -> None:
        self._magic_byte = magic_byte
        self._buffer = bytearray()

    def feed(self, chunk: bytes) -> list[bytes]:
        data = self._buffer + chunk
        messages: list[bytes] = []
        while True:
            try:
                position = data.index(self._magic_byte)
            except ValueError:
                break
            if len(data) < position + 2:
                break
            next_length = data[position + 1]
            expected_end = position + next_length + 2
            if len(data) < expected_end:
                break
            messages.append(bytes(data[position + 2 : expected_end]))
            data = data[expected_end:]
        self._buffer = bytearray(data)
        return messages

    def flush(self) -> bytes:
        remaining = bytes(self._buffer)
        self._buffer = bytearray()
        return remaining
