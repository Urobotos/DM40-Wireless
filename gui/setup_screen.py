"""Connect (cold run) – výběr DM40 v hlavním okně aplikace."""

from __future__ import annotations

import queue
import threading

import tkinter as tk

from ble.discovery import DM40Device, scan_dm40_devices_sync
from core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from gui import layout as L
from gui import setup_layout as SL
from gui.assets import bind_clickable, raise_click_hotspots
from gui.sprites import SpriteCache
from gui.theme import rgb_hex


class SetupScreen(tk.Frame):
    def __init__(self, master, app, scale: float) -> None:
        super().__init__(master, bg=rgb_hex("background"))
        self.app = app
        self.scale = scale
        self.sprites = SpriteCache()
        w, h = int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)
        self.configure(width=w, height=h)
        self.pack_propagate(False)

        self.canvas = tk.Canvas(self, width=w, height=h, highlightthickness=0, bg=rgb_hex("background"))
        self.canvas.pack()

        self._devices: list[DM40Device] = []
        self._selected = -1
        self._scanning = False
        self._scan_queue: queue.Queue = queue.Queue()
        self._sprite_ids: dict[str, int] = {}
        self._ble_pulse_on = True
        self._ble_pulse_after: str | None = None
        self._status_id: int | None = None

        self._draw_chrome()
        self._draw_bottom_buttons()

    def _s(self, v: float) -> int:
        return int(v * self.scale)

    def raise_click_layer(self) -> None:
        raise_click_hotspots(self.canvas)

    def _draw_chrome(self) -> None:
        self.canvas.create_rectangle(
            0, 0, self._s(L.SCREEN_W), self._s(L.TOP_BAR_H),
            fill=rgb_hex("top_bar_background"), outline="", tags="setup_chrome",
        )
        font = ("sans-serif", self._s(SL.SETUP_TITLE_FONT), "bold")
        self.canvas.create_text(
            self._s(L.SCREEN_W // 2), self._s(SL.SETUP_TITLE_Y), text="Connect",
            fill=rgb_hex("text_primary"), anchor="center", font=font, tags="setup_chrome",
        )
        hint_font = ("sans-serif", self._s(SL.SETUP_HINT_FONT), "normal")
        self.canvas.create_text(
            self._s(L.SCREEN_W // 2), self._s(SL.SETUP_HINT_Y),
            text="Enable Bluetooth on your DM40, then tap Search.",
            fill=rgb_hex("text_secondary"), anchor="center", font=hint_font, tags="setup_chrome",
        )
        status_font = ("sans-serif", self._s(SL.SETUP_STATUS_FONT), "normal")
        self._status_id = self.canvas.create_text(
            self._s(L.SCREEN_W // 2), self._s(SL.SETUP_STATUS_Y), text="",
            fill=rgb_hex("text_primary"), anchor="center", font=status_font, tags="setup_chrome",
        )
        self._set_status("Tap Search to find DM40A / DM40B / DM40C.")

    def _set_status(self, text: str) -> None:
        if self._status_id is not None:
            self.canvas.itemconfigure(self._status_id, text=text)

    def _top_bar_icon(self, name: str, max_w: int) -> tk.PhotoImage | None:
        return self.sprites.top_bar(
            name, self.scale,
            max_w=self._s(max_w), max_h=self._s(L.TOP_BAR_ICON_H),
        )

    def _show_sprite(self, key: str, photo: tk.PhotoImage, x: int, y: int) -> None:
        if key in self._sprite_ids:
            self.canvas.delete(self._sprite_ids[key])
        self._sprite_ids[key] = self.canvas.create_image(
            x, y, anchor="nw", image=photo, tags="setup_chrome",
        )

    def _hide_sprite(self, key: str) -> None:
        item = self._sprite_ids.pop(key, None)
        if item is not None:
            self.canvas.delete(item)

    def _show_bt_icon(self) -> None:
        photo = self._top_bar_icon("bluetooth.png", L.TOP_BAR_BT_W)
        if photo:
            self._show_sprite("bt", photo, self._s(L.BT_IMG[0]), self._s(L.BT_IMG[1]))

    def _stop_bt_pulse(self) -> None:
        if self._ble_pulse_after is not None:
            self.app.root.after_cancel(self._ble_pulse_after)
            self._ble_pulse_after = None

    def _bt_pulse_tick(self) -> None:
        if not self._scanning:
            return
        if self._ble_pulse_on:
            self._show_bt_icon()
        else:
            self._hide_sprite("bt")
        self._ble_pulse_on = not self._ble_pulse_on
        self._ble_pulse_after = self.app.root.after(550, self._bt_pulse_tick)

    def _start_bt_pulse(self) -> None:
        self._stop_bt_pulse()
        self._ble_pulse_on = True
        self._bt_pulse_tick()

    def _stop_scan_ui(self) -> None:
        self._scanning = False
        self._stop_bt_pulse()
        self._show_bt_icon()

    def _draw_bottom_buttons(self) -> None:
        font = ("sans-serif", self._s(13), "bold")
        for label, (x, y, w, h) in zip(SL.SETUP_BTN_LABELS, SL.setup_button_slots()):
            rx, ry, rw, rh = self._s(x), self._s(y), self._s(w), self._s(h)
            radius = self._s(L.MODE_BTN_RADIUS)
            photo = self.sprites.rounded_button("buttons", rw, rh, radius)
            if photo:
                self.canvas.create_image(
                    rx, ry, anchor="nw", image=photo, tags=("setup_btn", f"setup_btn_{label}"),
                )
            self.canvas.create_text(
                rx + rw // 2, ry + rh // 2, text=label,
                fill=rgb_hex("text_primary"), anchor="center", font=font,
                tags=("setup_btn", f"setup_btn_txt_{label}"),
            )
            cmd = self.start_scan if label == "Search" else self._on_connect
            bind_clickable(
                self.canvas, rx, ry, rw, rh, cmd, tag=f"setup_hit_{label}",
            )

    def on_show(self, *, auto_scan: bool = False) -> None:
        self._show_bt_icon()
        if auto_scan:
            self.app.root.after(300, self.start_scan)

    def on_hide(self) -> None:
        self._stop_scan_ui()

    def start_scan(self) -> None:
        if self._scanning:
            return
        self._scanning = True
        self._devices = []
        self._selected = -1
        self.canvas.delete("setup_row")
        self._set_status("Scanning for DM40A / DM40B / DM40C…")
        self._start_bt_pulse()
        threading.Thread(target=self._scan_worker, daemon=True).start()
        self._poll_scan_result()

    def _scan_worker(self) -> None:
        error: str | None = None
        devices: list[DM40Device] = []
        try:
            devices = scan_dm40_devices_sync(timeout=12.0)
        except Exception as exc:
            error = str(exc)
        self._scan_queue.put((devices, error))

    def _poll_scan_result(self) -> None:
        if not self.winfo_exists():
            return
        try:
            devices, error = self._scan_queue.get_nowait()
        except queue.Empty:
            if self._scanning:
                self.app.root.after(100, self._poll_scan_result)
            return
        self._scan_done(devices, error)

    def _scan_done(self, devices: list[DM40Device], error: str | None) -> None:
        self._stop_scan_ui()
        self._devices = devices
        self._selected = 0 if devices else -1
        self._rebuild_device_list()
        if error:
            self._set_status(f"Scan failed: {error}")
        elif not devices:
            self._set_status("No DM40 found. Enable Bluetooth on the meter and try Search again.")
        elif len(devices) == 1:
            self._set_status("1 device found – tap Connect.")
        else:
            self._set_status(f"{len(devices)} devices found – select one, then Connect.")

    def _rebuild_device_list(self) -> None:
        self.canvas.delete("setup_row")
        if not self._devices:
            self.raise_click_layer()
            return

        font = ("sans-serif", self._s(SL.SETUP_ROW_FONT), "normal")
        x = SL.SETUP_LIST_MARGIN
        w = L.SCREEN_W - 2 * SL.SETUP_LIST_MARGIN
        y = SL.SETUP_LIST_TOP
        bottom = SL.setup_list_bottom()
        row_h = SL.SETUP_ROW_H + SL.SETUP_ROW_GAP

        for i, dev in enumerate(self._devices):
            if y + SL.SETUP_ROW_H > bottom:
                break
            active = i == self._selected
            rx, ry, rw, rh = self._s(x), self._s(y), self._s(w), self._s(SL.SETUP_ROW_H)
            bg = "buttons_active" if active else "range_buttons"
            self.canvas.create_rectangle(
                rx, ry, rx + rw, ry + rh,
                fill=rgb_hex(bg), outline="", tags=("setup_row", f"setup_row_{i}"),
            )
            self.canvas.create_text(
                rx + self._s(SL.SETUP_ROW_PAD_LEFT), ry + rh // 2,
                text=dev.list_label(), anchor="w", font=font,
                fill=rgb_hex("text_primary"), tags=("setup_row", f"setup_txt_{i}"),
            )
            bind_clickable(
                self.canvas, rx, ry, rw, rh,
                lambda idx=i: self._select_device(idx), tag=f"setup_row_hit_{i}",
            )
            y += row_h

        self.raise_click_layer()

    def _select_device(self, index: int) -> None:
        if index < 0 or index >= len(self._devices):
            return
        self._selected = index
        self._rebuild_device_list()

    def _on_connect(self) -> None:
        if self._selected < 0 or self._selected >= len(self._devices):
            self._set_status("Select a device from the list first.")
            return
        self.app.complete_device_setup(self._devices[self._selected])
