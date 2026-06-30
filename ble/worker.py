"""Asyncio BLE worker – běží na pozadí, volá callbacky do GUI přes root.after."""

import asyncio
import threading
from dataclasses import dataclass
from typing import Callable

from bleak import BleakClient

from ble.bluetooth_radio import exception_indicates_bt_off, is_bluetooth_enabled
from core.config import (
    CMD_DISCOVERY,
    CMD_POLL,
    POLL_RESPONSE_TIMEOUT,
    TARGET_MAC,
    NOTIFY_UUID,
    WRITE_UUID,
)
from core.controller import create_command
from core.protocol_constants import CMD_ID
from core.parsing import (
    MODEL,
    guess_model_from_ble_name,
    parse_measurement_for_ui,
    range_label_from_packet,
    try_parse_model_packet,
)
from core.ranges import make_range_cmd


@dataclass
class BleCallbacks:
    on_connecting: Callable[[], None]
    on_connected: Callable[[], None]
    on_disconnected: Callable[[], None]
    on_bluetooth_off: Callable[[], None]
    on_model: Callable[[], None]
    on_measurement: Callable[[object, bytes], None]
    on_raw_traffic: Callable[[str, bytes], None] | None = None


class BleWorker:
    def __init__(self, callbacks: BleCallbacks, target_mac: str = TARGET_MAC) -> None:
        self._callbacks = callbacks
        self._target_mac = target_mac
        self._client = None
        self._loop = None
        self._poll_ready: asyncio.Event | None = None
        self._ble_lock: asyncio.Lock | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)

    @property
    def target_mac(self) -> str:
        return self._target_mac

    def set_target_mac(self, mac: str) -> None:
        self._target_mac = mac.strip()

    def start(self) -> None:
        self._thread.start()

    @property
    def connected(self) -> bool:
        return bool(self._client and self._client.is_connected)

    def send_command(self, payload: list[int]) -> None:
        self._schedule(self._write_gatt(create_command(payload)))

    def send_packet(self, packet: bytes) -> None:
        self._schedule(self._write_gatt(packet))

    def send_range_flag(self, flag: int) -> None:
        self.send_packet(make_range_cmd(flag))

    def _schedule(self, coro) -> None:
        if self._loop and self._client and self._client.is_connected:
            asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _run(self) -> None:
        asyncio.run(self._ble_loop())

    def _emit_raw(self, direction: str, data: bytes) -> None:
        if self._callbacks.on_raw_traffic:
            self._callbacks.on_raw_traffic(direction, data)

    async def _write_gatt(self, packet: bytes, *, wait_notify: bool = True) -> None:
        if not self._client or not self._client.is_connected or self._ble_lock is None:
            return
        self._emit_raw("TX", packet)
        async with self._ble_lock:
            await self._client.write_gatt_char(WRITE_UUID, packet)
            if not wait_notify or self._poll_ready is None:
                return
            self._poll_ready.clear()
            try:
                await asyncio.wait_for(self._poll_ready.wait(), timeout=0.5)
            except asyncio.TimeoutError:
                pass

    async def _ble_loop(self) -> None:
        while True:
            if not (self._target_mac or "").strip():
                await asyncio.sleep(0.5)
                continue
            bt_on = is_bluetooth_enabled()
            if bt_on is False:
                self._callbacks.on_bluetooth_off()
                await asyncio.sleep(2.0)
                continue

            try:
                print(f"Hledam zarizeni {self._target_mac}...")
                self._callbacks.on_connecting()
                async with BleakClient(self._target_mac, timeout=20.0) as client:
                    self._client = client
                    self._loop = asyncio.get_running_loop()
                    print("Pripojeno.")
                    if guess_model_from_ble_name(client.name or ""):
                        self._callbacks.on_model()

                    self._poll_ready = asyncio.Event()
                    self._ble_lock = asyncio.Lock()
                    await client.start_notify(NOTIFY_UUID, self._on_notify)
                    self._emit_raw("TX", CMD_DISCOVERY)
                    await client.write_gatt_char(WRITE_UUID, CMD_DISCOVERY)
                    await self._write_gatt(CMD_ID)
                    self._callbacks.on_connected()

                    while client.is_connected:
                        async with self._ble_lock:
                            self._poll_ready.clear()
                            self._emit_raw("TX", CMD_POLL)
                            await client.write_gatt_char(WRITE_UUID, CMD_POLL)
                            try:
                                await asyncio.wait_for(
                                    self._poll_ready.wait(),
                                    timeout=POLL_RESPONSE_TIMEOUT,
                                )
                            except asyncio.TimeoutError:
                                pass
                    await asyncio.sleep(0.01)
            except Exception as exc:
                print(f"Chyba/Odpojeno: {exc}. Pripojuji znova...")
                self._client = None
                self._ble_lock = None
                if exception_indicates_bt_off(exc):
                    self._callbacks.on_bluetooth_off()
                    await asyncio.sleep(2.0)
                else:
                    self._callbacks.on_disconnected()
                    await asyncio.sleep(1)

    def _on_notify(self, _sender, data: bytes) -> None:
        self._emit_raw("RX", data)
        if self._poll_ready is not None and self._loop is not None:
            self._loop.call_soon_threadsafe(self._poll_ready.set)

        if try_parse_model_packet(data):
            self._callbacks.on_model()
            return

        m = parse_measurement_for_ui(data)
        if m.kind == "---":
            return
        self._callbacks.on_measurement(m, data)
