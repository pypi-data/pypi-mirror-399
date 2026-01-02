from __future__ import annotations

from .serial import LoupedeckSerialConnection
from .ws import LoupedeckWebSocketConnection

__all__ = ["LoupedeckSerialConnection", "LoupedeckWebSocketConnection"]
