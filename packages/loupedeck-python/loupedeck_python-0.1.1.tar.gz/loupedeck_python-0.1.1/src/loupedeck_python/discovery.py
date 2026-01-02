from __future__ import annotations

from typing import Any

from .device import (
    LoupedeckCT,
    LoupedeckLive,
    LoupedeckLiveS,
    LoupedeckDevice,
    RazerStreamController,
    RazerStreamControllerX,
)


async def discover(*, auto_connect: bool = True, **device_kwargs: Any) -> LoupedeckDevice:
    devices = await LoupedeckDevice.list()
    if not devices:
        raise RuntimeError("No devices found")
    info = devices[0]
    device_cls = _device_type_for_product(info.product_id)
    if not device_cls:
        raise RuntimeError(
            f"Device with product ID {info.product_id} not supported yet"
        )
    kwargs = dict(device_kwargs)
    kwargs["auto_connect"] = auto_connect
    if info.path:
        kwargs["path"] = info.path
    if info.host:
        kwargs["host"] = info.host
    return device_cls(**kwargs)


def _device_type_for_product(product_id: int) -> type[LoupedeckDevice] | None:
    for device_cls in (
        LoupedeckLive,
        LoupedeckCT,
        LoupedeckLiveS,
        RazerStreamController,
        RazerStreamControllerX,
    ):
        if getattr(device_cls, "product_id", None) == product_id:
            return device_cls
    return None
