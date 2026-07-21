"""Main application window – Main / Range / Settings screen switching."""

import time

import tkinter as tk

from ble.worker import BleCallbacks, BleWorker
from core.config import CMD_DISCOVERY, CMD_POLL
from core.protocol_constants import CMD_ID
from core.i18n import t, get_i18n
from gui import layout as display_layout
from core.modes import MODE_CYCLE_GROUPS, ModeState
from core.parsing import MODEL, range_label_from_packet
from gui.main_screen import MainScreen
from gui.range_screen import RangeScreen
from gui.raw_console import RawConsole
from gui.settings import load_settings, apply_saved_model, save_settings, persist_device
from gui.setup_screen import SetupScreen
from gui.settings_screen import SettingsScreen
from gui.theme import rgb_hex
from gui.win_titlebar import fit_toplevel_to_client, schedule_windows_titlebar

_BACKGROUND_TX = frozenset({CMD_DISCOVERY, CMD_POLL, CMD_ID})


class DM40App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.settings = load_settings()
        apply_saved_model(self.settings)

        # Initialize i18n from language in settings.json
        lang = (self.settings.get("language") or "").strip() or "en-US"
        get_i18n().init(lang)
        self.scale = float(self.settings.get("window_scale", 1.0))
        self.mode_state = ModeState()
        for gid, opts in MODE_CYCLE_GROUPS:
            self.mode_state.register_group(gid, opts)
        self.mode_state.load()

        self._current_screen = "main"
        self._client_w = int(display_layout.SCREEN_W * self.scale)

        self.root.title(t("app.title"))
        self.root.resizable(False, False)
        self.root.configure(bg=rgb_hex("background"))

        self._ui_column = tk.Frame(root, bg=rgb_hex("background"))
        self._ui_column.pack()

        dm40_h = self._dm40_logical_height()
        self._client_dm40_h = int(dm40_h * self.scale)
        self.container = tk.Frame(
            self._ui_column, bg=rgb_hex("background"),
            width=self._client_w, height=self._client_dm40_h,
        )
        self.container.pack_propagate(False)
        self.container.pack()

        self.raw_console = RawConsole(self._ui_column, self.scale)

        self._readings: list[str] = []
        self._last_range_flag = 0
        self._raw_rx_burst_until = 0.0
        self._last_raw_line = ""
        self._raw_poll_pending: str | None = None
        self._raw_poll_after: str | None = None
        self._meas_pending: tuple[object, bytes] | None = None
        self._meas_scheduled = False
        self._ble_started = False

        cbs = BleCallbacks(
            on_connecting=self._on_connecting,
            on_connected=self._on_connected,
            on_disconnected=self._on_disconnected,
            on_bluetooth_off=self._on_bluetooth_off,
            on_model=self._on_model,
            on_measurement=self._on_measurement,
            on_raw_traffic=self._on_raw_traffic,
        )
        self.ble = BleWorker(cbs, target_mac=self.settings.get("target_mac", ""))

        self.main_screen = MainScreen(self.container, self, self.scale)
        self.range_screen = RangeScreen(self.container, self, self.scale)
        self.settings_screen = SettingsScreen(self.container, self, self.scale)
        self.setup_screen = SetupScreen(self.container, self, self.scale)
        place_kw = dict(x=0, y=0, width=self._client_w, height=self._client_dm40_h)
        for screen in (
            self.main_screen, self.range_screen, self.settings_screen, self.setup_screen,
        ):
            screen.place(**place_kw)

        self.main_screen.refresh_mode_buttons(self.mode_state)
        schedule_windows_titlebar(self.root)
        if self._needs_device_setup():
            self.show_setup_screen(auto_scan=True)
        else:
            self.show_main_screen()
            self._sync_raw_callback()
            self.ble.start()
            self._ble_started = True

    def _needs_device_setup(self) -> bool:
        return not (self.settings.get("target_mac") or "").strip()

    def complete_device_setup(self, device) -> None:
        from core.parsing import apply_model

        apply_model(device.model_name, device.device_counts)
        self.settings["target_mac"] = device.address
        self.settings["model_name"] = device.model_name
        self.settings["device_counts"] = device.device_counts
        save_settings(self.settings)
        self.ble.set_target_mac(device.address)
        if not self._ble_started:
            self.ble.start()
            self._ble_started = True
        self.setup_screen.on_hide()
        self.show_main_screen()

    def reload_language(self, lang_code: str) -> None:
        """Switch language, refresh all screens, and update settings.json."""
        i18n = get_i18n()
        if not i18n.load_language(lang_code):
            return
        # Atomic settings.json write (.tmp then replace, prevents corruption)
        self.settings["language"] = lang_code
        from gui.settings import save_settings
        if not save_settings(self.settings):
            # Save failure does not block UI refresh; in-memory language still applies this session
            pass
        # Refresh UI
        self.root.title(t("app.title"))
        self._refresh_all_screens_i18n()

    def _refresh_all_screens_i18n(self) -> None:
        """Refresh translatable strings on every screen (language is switched from Settings)."""
        self.main_screen.refresh_all()
        kind = self.mode_state.get_active_kind()
        self.range_screen.rebuild_for_kind(kind, self._last_range_flag)
        self.settings_screen.rebuild()
        self.setup_screen.refresh_all()
        self._apply_window_size()

    def show_setup_screen(self, *, auto_scan: bool = False) -> None:
        self._current_screen = "setup"
        self.main_screen.lower()
        self.range_screen.lower()
        self.settings_screen.lower()
        self.setup_screen.lift()
        self.apply_settings()
        self.setup_screen.on_show(auto_scan=auto_scan)
        self.setup_screen.raise_click_layer()

    def _sync_raw_callback(self) -> None:
        """Without RAW console, do not call callback from BLE thread (every poll TX+RX)."""
        self.ble._callbacks.on_raw_traffic = (
            self._on_raw_traffic if self.settings.get("raw_console") else None
        )

    def _dm40_logical_height(self) -> int:
        if self._current_screen == "main" and self.settings.get("mini_app"):
            return display_layout.MINI_SCREEN_H
        return display_layout.SCREEN_H

    def _client_dimensions(self) -> tuple[int, int]:
        h = int(self._dm40_logical_height() * self.scale)
        if self._current_screen == "main" and self.settings.get("raw_console"):
            h += int(display_layout.RAW_CONSOLE_H * self.scale)
        return self._client_w, h

    def _apply_window_size(self) -> None:
        """Client area = DM40 UI (+ RAW console); no empty strip below content."""
        self.root.update_idletasks()
        self.root.update()
        w, h = self._client_dimensions()
        fit_toplevel_to_client(self.root, self._ui_column, w, h)

    def _resize_container(self) -> None:
        dm40_h = self._dm40_logical_height()
        self._client_dm40_h = int(dm40_h * self.scale)
        self.container.configure(width=self._client_w, height=self._client_dm40_h)
        place_kw = dict(x=0, y=0, width=self._client_w, height=self._client_dm40_h)
        for screen in (
            self.main_screen, self.range_screen, self.settings_screen, self.setup_screen,
        ):
            screen.place(**place_kw)
        if self._current_screen == "main":
            self.main_screen.resize_to_logical_height(dm40_h)

    def _update_raw_console_visibility(self) -> None:
        show = self._current_screen == "main" and bool(self.settings.get("raw_console"))
        if show:
            self.raw_console.pack(fill="x", after=self.container)
        else:
            self.raw_console.pack_forget()
            self._raw_poll_pending = None
            self._cancel_raw_poll_tick()

    def apply_settings(self) -> None:
        self.root.attributes("-topmost", bool(self.settings.get("always_on_top", False)))
        mini = bool(self.settings.get("mini_app", False))
        self.main_screen.apply_view_mode(mini=mini, resize=self._current_screen == "main")
        if not self.settings.get("raw_console"):
            self._raw_poll_pending = None
            self._cancel_raw_poll_tick()
        self._sync_raw_callback()
        self._update_raw_console_visibility()
        self._resize_container()
        self._apply_window_size()

    @staticmethod
    def _format_raw_line(direction: str, data: bytes) -> str:
        hex_str = data.hex(" ").upper()
        if direction == "RX":
            crc = "PASS" if (sum(data) & 0xFF) == 0 else "FAIL"
            return f"RX {hex_str}  CRC:{crc}\n"
        return f"TX {hex_str}\n"

    def _is_priority_raw(self, direction: str, data: bytes) -> bool:
        """User TX (MODE, RANGE, HOLD, …) + short RX response."""
        if direction == "TX":
            return data not in _BACKGROUND_TX
        return direction == "RX" and time.monotonic() < self._raw_rx_burst_until

    def _append_raw_line(self, line: str, *, priority: bool) -> None:
        if not self.settings.get("raw_console") or self._current_screen != "main":
            return
        if priority:
            self._raw_poll_pending = None
            self._cancel_raw_poll_tick()
        elif line == self._last_raw_line:
            return
        self._last_raw_line = line
        self.raw_console.append(line)
        if priority and line.startswith("TX "):
            self._raw_rx_burst_until = time.monotonic() + 0.6

    def _cancel_raw_poll_tick(self) -> None:
        if self._raw_poll_after is not None:
            self.root.after_cancel(self._raw_poll_after)
            self._raw_poll_after = None

    def _schedule_raw_poll_tick(self) -> None:
        if self._raw_poll_after is None:
            self._raw_poll_after = self.root.after(
                display_layout.RAW_CONSOLE_POLL_MS, self._emit_raw_poll_line,
            )

    def _queue_raw_poll_line(self, line: str) -> None:
        """Poll: throttled output, no queue – keeps only the latest unshown line."""
        if line == self._last_raw_line:
            return
        self._raw_poll_pending = line
        self._schedule_raw_poll_tick()

    def _emit_raw_poll_line(self) -> None:
        self._raw_poll_after = None
        if not self.settings.get("raw_console") or self._current_screen != "main":
            self._raw_poll_pending = None
            return
        line = self._raw_poll_pending
        if line is None:
            return
        self._raw_poll_pending = None
        if line != self._last_raw_line:
            self._last_raw_line = line
            self.raw_console.append(line)
        if self._raw_poll_pending is not None:
            self._schedule_raw_poll_tick()

    def _on_raw_traffic(self, direction: str, data: bytes) -> None:
        line = self._format_raw_line(direction, data)
        if self._is_priority_raw(direction, data):
            self.root.after(0, lambda l=line: self._append_raw_line(l, priority=True))
            return
        self._queue_raw_poll_line(line)

    def show_main_screen(self) -> None:
        self._current_screen = "main"
        self.range_screen.lower()
        self.settings_screen.lower()
        self.setup_screen.lower()
        self.main_screen.lift()
        self.apply_settings()
        self.main_screen.raise_click_layer()

    def show_range_screen(self) -> None:
        self._current_screen = "range"
        kind = self.mode_state.get_active_kind()
        self.range_screen.rebuild_for_kind(kind, self._last_range_flag)
        self.main_screen.lower()
        self.settings_screen.lower()
        self.setup_screen.lower()
        self.range_screen.lift()
        self.apply_settings()
        self.range_screen.raise_click_layer()

    def show_settings_screen(self) -> None:
        self._current_screen = "settings"
        self.settings_screen.rebuild()
        self.main_screen.lower()
        self.range_screen.lower()
        self.setup_screen.lower()
        self.settings_screen.lift()
        self.apply_settings()
        self.settings_screen.raise_click_layer()

    def cycle_mode(self, group_id: str) -> None:
        self.main_screen.release_hold_freeze()
        self.ble.send_packet(self.mode_state.cycle_group(group_id))
        self.main_screen.refresh_mode_buttons(self.mode_state)
        self.main_screen.raise_click_layer()

    def capture_reading(self) -> None:
        pass

    def _on_connecting(self) -> None:
        self.root.after(0, lambda: self.main_screen.set_ble_connection_state("connecting"))

    def _on_connected(self) -> None:
        def ui() -> None:
            self.main_screen.set_ble_connection_state("connected")
            self._persist_device_from_session()

        self.root.after(0, ui)

    def _on_disconnected(self) -> None:
        self.root.after(0, lambda: self.main_screen.set_ble_connection_state("disconnected"))

    def _on_bluetooth_off(self) -> None:
        self.root.after(0, lambda: self.main_screen.show_bluetooth_off())

    def _on_model(self) -> None:
        def ui() -> None:
            self.main_screen.set_ble_connection_state("connected")
            self._persist_device_from_session()

        self.root.after(0, ui)

    def _persist_device_from_session(self) -> None:
        persist_device(
            self.settings,
            mac=self.ble.target_mac,
            model_name=MODEL.model_name,
            device_counts=MODEL.device_counts,
        )

    def _on_measurement(self, m, data: bytes) -> None:
        self._meas_pending = (m, data)
        if not self._meas_scheduled:
            self._meas_scheduled = True
            self.root.after(0, self._flush_measurement)

    def _flush_measurement(self) -> None:
        self._meas_scheduled = False
        pending = self._meas_pending
        if pending is None:
            return
        self._meas_pending = None
        m, data = pending
        if len(data) > 5:
            self._last_range_flag = data[5]
        if not m.hold:
            self.mode_state.last_kind = m.kind
            if self.mode_state.sync_from_kind(m.kind):
                self.main_screen.refresh_mode_buttons(self.mode_state)
        rng = range_label_from_packet(data, m.range)
        trace_key = data[5] if len(data) > 5 else 0
        self.main_screen.update_measurement(m, rng, trace_key)


def run_app() -> None:
    root = tk.Tk()
    DM40App(root)
    root.mainloop()
