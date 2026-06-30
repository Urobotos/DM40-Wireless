"""Vyhledání DM40 multimetrů přes BLE (Bleak)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from bleak import BleakScanner

from core.protocol_constants import MODEL_TABLE


@dataclass(frozen=True)
class DM40Device:
    address: str
    name: str
    model_name: str
    device_counts: int

    def list_label(self) -> str:
        return f"{self.name or self.model_name}  ({self.address})"


def model_from_ble_name(name: str) -> tuple[str, int] | None:
    upper = (name or "").upper()
    for model_name, device_counts in MODEL_TABLE:
        if model_name in upper:
            return model_name, device_counts
    return None


async def scan_dm40_devices(*, timeout: float = 10.0) -> list[DM40Device]:
    """Vrátí nalezená DM40A/B/C zařízení (podle BLE jména)."""
    found: dict[str, DM40Device] = {}
    try:
        discovered = await BleakScanner.discover(timeout=timeout, return_adv=True)
        items = discovered.items()
    except TypeError:
        devices = await BleakScanner.discover(timeout=timeout)
        items = ((d.address, (d, None)) for d in devices)

    for address, (device, adv) in items:
        name = device.name or (getattr(adv, "local_name", None) if adv else None) or ""
        parsed = model_from_ble_name(name)
        if parsed is None:
            continue
        model_name, device_counts = parsed
        key = address.upper()
        if key not in found:
            found[key] = DM40Device(
                address=address,
                name=name.strip(),
                model_name=model_name,
                device_counts=device_counts,
            )
    return sorted(found.values(), key=lambda d: d.name or d.address)


def scan_dm40_devices_sync(*, timeout: float = 10.0) -> list[DM40Device]:
    return asyncio.run(scan_dm40_devices(timeout=timeout))
