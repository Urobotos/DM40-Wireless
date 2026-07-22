"""Main multimeter screen – sprite GUI without full-screen PNG background."""

import tkinter as tk

from core.aux_display import AuxPanel, build_aux_panels
from core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from core.i18n import t
from core.controller import COMMANDS
from gui.graph_panel import GraphPanel
from core.display_format import combined_main_value_str, split_main_value
from core.hv_warning import HV_WARNING_IMAGE, is_high_voltage_warning
from core.save_slots import SAVE_SLOT_COUNT, SaveSlotManager, format_save_reading
from core.save_units import save_unit_sprite_filename
from core.modes import MODE_CYCLE_GROUPS
from core.parsing import MODEL
from gui import layout as L
from gui.assets import CLICK_HOTSPOT_TAG, bind_clickable, raise_click_hotspots
from gui.display_debug import clear_display_debug, draw_debug_rect
from gui.sprites import SpriteCache, main_unit_filename
from gui.theme import rgb_hex

class MainScreen(tk.Frame):
    def __init__(self, master, app, scale: float) -> None:
        super().__init__(master, bg=rgb_hex("background"))
        self.app = app
        self.scale = scale
        self.sprites = SpriteCache()
        self._mini_mode = bool(getattr(app, "settings", {}).get("mini_app", False))
        self._logical_h = L.dm40_main_height(mini=self._mini_mode)
        w, h = int(SCREEN_WIDTH * scale), int(self._logical_h * scale)
        self.configure(width=w, height=h)
        self.pack_propagate(False)

        self.canvas = tk.Canvas(self, width=w, height=h, highlightthickness=0, bg=rgb_hex("background"))
        self.canvas.pack()

        self._text_ids: dict[str, int] = {}
        self._sprite_ids: dict[str, int] = {}
        self._mode_btn_ids: list[str] = []
        self._last_range_label = ""
        self._last_hold: bool | None = None
        self._ble_state = "disconnected"
        self._ble_pulse_on = True
        self._ble_pulse_after_id: str | None = None
        self._bt_off_display = False
        self._hv_warning_active = False
        self._display_frozen = False
        self._last_display_measurement: tuple | None = None
        self._save_slots = SaveSlotManager()
        self._long_press_after: str | None = None
        self._long_press_fired = False
        self._last_locked: bool | None = None
        self._last_battery: tuple[int, bool] | None = None
        self._last_unit_key: tuple[str, str] | None = None
        self._aux_cache: dict[str, tuple] = {}
        self._graph = GraphPanel(
            self.canvas, self._s, self.sprites,
            on_ble_command=self.app.ble.send_command,
            root=app.root,
        )
        settings = getattr(app, "settings", {})
        self._debug_hotspots = bool(settings.get("debug_click_hotspots", False))
        self._debug_display = bool(settings.get("debug_display_layout", False))

        self._draw_chrome()
        self._graph.install()
        self._draw_mode_buttons()
        self.apply_view_mode(mini=self._mini_mode)
        self._raise_visual_layers()
        self._bind_hotspots()

    def raise_click_layer(self) -> None:
        self._raise_visual_layers()
        raise_click_hotspots(self.canvas)
        self.canvas.tag_raise("graph_hit_rel")

    def _raise_visual_layers(self) -> None:
        """Graph below MODE row; click zones handled in raise_click_layer."""
        self.canvas.tag_lower("graph")
        self.canvas.tag_raise("mode_btn")

    def _s(self, v: float) -> int:
        return int(v * self.scale)

    def _main_value_font(self) -> tuple[str, int, str]:
        return ("sans-serif", self._s(L.MAIN_VALUE_FONT), "bold")

    def _bt_off_font(self) -> tuple[str, int, str]:
        return ("sans-serif", self._s(L.MAIN_BT_OFF_FONT), "bold")

    def _main_row_cy(self) -> int:
        return self._s(L.MAIN_VALUE_ROW_CY)

    def _set_canvas_text(self, key: str, text: str) -> None:
        item = self._text_ids.get(key)
        if item is not None:
            self.canvas.itemconfig(item, text=text)

    def _hide_sprite(self, key: str) -> None:
        item = self._sprite_ids.pop(key, None)
        if item is not None:
            self.canvas.delete(item)

    def _show_sprite(self, key: str, photo: tk.PhotoImage, x: int, y: int, anchor: str = "nw") -> None:
        if key in self._sprite_ids:
            self.canvas.delete(self._sprite_ids[key])
        self._sprite_ids[key] = self.canvas.create_image(x, y, anchor=anchor, image=photo, tags="sprite")

    def _top_bar_status_font(self) -> tuple[str, int, str]:
        return ("sans-serif", self._s(L.TOP_BAR_STATUS_FONT), "")

    def _top_bar_status_y(self, img_y: float) -> int:
        return self._s(img_y + L.TOP_BAR_STATUS_Y_OFFSET)

    def _draw_chrome(self) -> None:
        s = self.scale
        self.canvas.create_rectangle(
            0, 0, self._s(L.SCREEN_W), self._s(L.TOP_BAR_H),
            fill=rgb_hex("top_bar_background"), outline="",
        )
        for i, (sx, sy, sw, sh) in enumerate(L.save_slot_slots()):
            rx, ry, rw, rh = self._s(sx), self._s(sy), self._s(sw), self._s(sh)
            radius = self._s(L.SAVE_SLOT_RADIUS)
            photo = self.sprites.rounded_button("save_area", rw, rh, radius)
            if photo:
                self.canvas.create_image(
                    rx, ry, anchor="nw", image=photo,
                    tags=("save_slot_bg", f"save_slot_bg_{i}"),
                )
            else:
                self.canvas.create_rectangle(
                    rx, ry, rx + rw, ry + rh,
                    fill=rgb_hex("save_area"), outline="", tags="save_slot_bg",
                )
        font_main = self._main_value_font()
        font_sec = ("sans-serif", self._s(L.SEC_FONT), "bold")
        layout = L.main_value_layout()
        sign_x, _, sign_w, _ = layout["sign"]
        digits_x, _, digits_w, _ = layout["digits"]
        lx, ly = L.SEC_LEFT
        rx, ry = L.SEC_RIGHT

        self._text_ids["aux_left"] = self.canvas.create_text(
            self._s(lx), self._s(ly), text="", fill=rgb_hex("orange_main"),
            anchor="w", font=font_sec,
        )
        self._text_ids["aux_right"] = self.canvas.create_text(
            self._s(rx), self._s(ry), text="", fill=rgb_hex("orange_main"),
            anchor="w", font=font_sec,
        )
        cy = self._main_row_cy()
        self._text_ids["value_sign"] = self.canvas.create_text(
            self._s(sign_x + sign_w // 2), cy, text=" ",
            fill=rgb_hex("orange_main"), anchor="center", font=font_main,
        )
        self._text_ids["value_digits"] = self.canvas.create_text(
            self._s(digits_x + digits_w // 2), cy, text="---",
            fill=rgb_hex("orange_main"), anchor="center", font=font_main,
        )
        top_font = self._top_bar_status_font()
        self._text_ids["range_text"] = self.canvas.create_text(
            self._s(L.RANGE_IMG[0]), self._top_bar_status_y(L.RANGE_IMG[1]), text="AUTO+",
            fill=rgb_hex("text_primary"), anchor="w", font=top_font,
        )
        self._text_ids["hold_text"] = self.canvas.create_text(
            self._s(L.HOLD_IMG[0]), self._top_bar_status_y(L.HOLD_IMG[1]), text="RUN",
            fill=rgb_hex("text_primary"), anchor="w", font=top_font,
        )

        save_font = ("sans-serif", self._s(L.SAVE_FONT), "bold")
        for i in range(SAVE_SLOT_COUNT):
            self._text_ids[f"save_{i}"] = self.canvas.create_text(
                0, 0, text="", anchor="w", font=save_font,
                fill=rgb_hex("text_primary"), tags="save_slot",
            )

        self._set_range_display("AUTO+")
        self._set_hold_display(False, force=True)
        self._set_settings_display()
        self._set_lock_display(False)
        self._set_battery_display(0, False)
        self.set_ble_connection_state("connecting")
        self._draw_display_debug_regions()

    def _draw_display_debug_regions(self) -> None:
        clear_display_debug(self.canvas)
        if not self._debug_display:
            return
        s = self.scale
        colors = {
            "row": "#404080",
            "hv_warn": "#804080",
            "sign": "#c04040",
            "digits": "#40a060",
            "units": "#a0a040",
            "aux_row": "#40a0a0",
        }
        for name, rect in L.main_value_layout().items():
            x, y, w, h = rect
            draw_debug_rect(self.canvas, x, y, w, h, colors.get(name, "#808080"), scale=s)
        for name, rect in L.aux_debug_layout().items():
            x, y, w, h = rect
            draw_debug_rect(self.canvas, x, y, w, h, colors["aux_row"], scale=s)
        for i, (x, y, w, h) in enumerate(L.save_slot_slots()):
            draw_debug_rect(self.canvas, x, y, w, h, "#8060a0", scale=s)

    def _set_main_value_color(self, hv_warning: bool) -> None:
        color = rgb_hex("orange_hv_warn") if hv_warning else rgb_hex("orange_main")
        for key in ("value_sign", "value_digits"):
            item = self._text_ids.get(key)
            if item is not None:
                self.canvas.itemconfig(item, fill=color)

    def _update_hv_warning(self, active: bool) -> None:
        self._hv_warning_active = active
        self._set_main_value_color(active)
        if not active or L.MAIN_HV_WARN_W <= 0:
            self._hide_sprite("hv_warn")
            return
        layout = L.main_value_layout()
        hx, hy, hw, hh = layout["hv_warn"]
        photo = self.sprites.main_unit_sprite(
            HV_WARNING_IMAGE, self.scale, max_w=self._s(hw), max_h=self._s(hh),
        )
        if photo:
            self._show_sprite(
                "hv_warn", photo,
                self._s(hx + hw // 2), self._s(hy + hh // 2),
                anchor="center",
            )
        else:
            self._hide_sprite("hv_warn")

    def _layout_main_value(self, raw: str, decimals: int = 2) -> None:
        if raw == t("main.bt_off"):
            layout = L.main_value_layout()
            rx, _, rw, _ = layout["row"]
            self._set_canvas_text("value_sign", "")
            self.canvas.coords(self._text_ids["value_digits"], self._s(rx + rw // 2), self._main_row_cy())
            self.canvas.itemconfig(
                self._text_ids["value_digits"],
                text=raw, anchor="center", font=self._bt_off_font(),
            )
            self._set_main_value_color(False)
            return

        main_font = self._main_value_font()
        self.canvas.itemconfig(self._text_ids["value_digits"], font=main_font)
        self.canvas.itemconfig(self._text_ids["value_sign"], font=main_font)

        sign, body, mode = split_main_value(raw, decimals)
        layout = L.main_value_layout()
        sign_x, _, sign_w, _ = layout["sign"]
        digits_x, _, digits_w, _ = layout["digits"]
        cy = self._main_row_cy()

        if mode == "ol":
            self._set_canvas_text("value_sign", "")
            self.canvas.coords(
                self._text_ids["value_digits"],
                self._s(digits_x + digits_w // 2), cy,
            )
            self.canvas.itemconfig(self._text_ids["value_digits"], text="OL", anchor="center")
            return

        if mode == "text":
            self._set_canvas_text("value_sign", "")
            self.canvas.coords(
                self._text_ids["value_digits"],
                self._s(digits_x + digits_w // 2), cy,
            )
            self.canvas.itemconfig(self._text_ids["value_digits"], text=body, anchor="center")
            return

        self.canvas.coords(self._text_ids["value_sign"], self._s(sign_x + sign_w // 2), cy)
        self.canvas.itemconfig(self._text_ids["value_sign"], text=sign, anchor="center")
        self.canvas.coords(
            self._text_ids["value_digits"],
            self._s(digits_x + digits_w // 2), cy,
        )
        self.canvas.itemconfig(self._text_ids["value_digits"], text=body, anchor="center")

    def _top_bar_icon(self, name: str, max_w: int) -> tk.PhotoImage | None:
        return self.sprites.top_bar(
            name, self.scale,
            max_w=self._s(max_w), max_h=self._s(L.TOP_BAR_ICON_H),
        )

    def _set_range_display(self, label: str) -> None:
        self._last_range_label = label
        self._hide_sprite("range")
        self._set_canvas_text("range_text", label)

    def _set_hold_display(self, hold: bool, *, force: bool = False) -> None:
        if not force and hold == self._last_hold:
            return
        self._last_hold = hold
        self._hide_sprite("hold_run")
        self._set_canvas_text("hold_text", "HOLD" if hold else "RUN")

    def _set_settings_display(self) -> None:
        photo = self._top_bar_icon("settings.png", L.TOP_BAR_SETTINGS_W)
        if photo:
            self._show_sprite(
                "settings", photo,
                self._s(L.SETTINGS_IMG[0]), self._s(L.SETTINGS_IMG[1]),
            )

    def _set_lock_display(self, locked: bool) -> None:
        if locked == self._last_locked:
            return
        self._last_locked = locked
        name = "screen_locked.png" if locked else "screen_unlocked.png"
        photo = self._top_bar_icon(name, L.TOP_BAR_LOCK_W)
        if photo:
            self._show_sprite("lock", photo, self._s(L.LOCK_IMG[0]), self._s(L.LOCK_IMG[1]))
        elif locked:
            self._hide_sprite("lock")

    def _set_battery_display(self, bars: int, charging: bool) -> None:
        state = (bars, charging)
        if state == self._last_battery:
            return
        self._last_battery = state
        photo = self.sprites.battery_sprite(
            bars, charging, self.scale,
            max_w=self._s(L.TOP_BAR_BATTERY_W), max_h=self._s(L.TOP_BAR_ICON_H),
        )
        if photo:
            self._show_sprite("battery", photo, self._s(L.BATTERY_IMG[0]), self._s(L.BATTERY_IMG[1]))

    def _show_bt_icon(self) -> None:
        photo = self._top_bar_icon("bluetooth.png", L.TOP_BAR_BT_W)
        if photo:
            self._show_sprite("bt", photo, self._s(L.BT_IMG[0]), self._s(L.BT_IMG[1]))

    def _stop_ble_pulse(self) -> None:
        if self._ble_pulse_after_id is not None:
            self.app.root.after_cancel(self._ble_pulse_after_id)
            self._ble_pulse_after_id = None

    def _ble_pulse_tick(self) -> None:
        if self._ble_state != "connecting":
            return
        if self._ble_pulse_on:
            self._show_bt_icon()
        else:
            self._hide_sprite("bt")
        self._ble_pulse_on = not self._ble_pulse_on
        self._ble_pulse_after_id = self.app.root.after(550, self._ble_pulse_tick)

    def show_bluetooth_off(self) -> None:
        self._bt_off_display = True
        self._stop_ble_pulse()
        self._ble_state = "disconnected"
        self._hide_sprite("bt")
        self._layout_main_value(t("main.bt_off"))
        self._update_hv_warning(False)
        self._clear_aux_displays()
        self._clear_unit_sprites()
        self._draw_display_debug_regions()
        self.raise_click_layer()

    def set_ble_connection_state(self, state: str) -> None:
        if state in ("connecting", "connected"):
            self._bt_off_display = False
        self._ble_state = state
        self._stop_ble_pulse()
        if state == "connecting":
            if not self._bt_off_display:
                self._layout_main_value("---")
                self._update_hv_warning(False)
            self._ble_pulse_on = True
            self._ble_pulse_tick()
        elif state == "connected":
            self._show_bt_icon()
        else:
            self._hide_sprite("bt")
        self.raise_click_layer()

    def _clear_unit_sprites(self) -> None:
        self._hide_sprite("main_unit")

    def _clear_aux_displays(self) -> None:
        self._aux_cache.clear()
        self._set_canvas_text("aux_left", "")
        self._set_canvas_text("aux_right", "")
        for key in ("aux_left_unit", "aux_left_char", "aux_right_unit", "aux_right_char"):
            self._hide_sprite(key)

    def _aux_sprite_width(self, fname: str | None) -> int:
        if not fname:
            return 0
        photo = self.sprites.display_unit_aux(fname, self.scale, max_h=self._s(L.AUX_ICON_MAX_H))
        return photo.width() if photo else 0

    def _place_aux_sprite(self, key: str, fname: str | None, x: int, y: int, anchor: str) -> int:
        if not fname:
            self._hide_sprite(key)
            return 0
        photo = self.sprites.display_unit_aux(fname, self.scale, max_h=self._s(L.AUX_ICON_MAX_H))
        if not photo:
            self._hide_sprite(key)
            return 0
        self._show_sprite(key, photo, x, y, anchor=anchor)
        return photo.width()

    def _layout_aux_row(self, text_key: str, unit_key: str, char_key: str, panel: AuxPanel, start_x: int, y: int) -> None:
        gap = self._s(L.AUX_ICON_GAP)
        text_id = self._text_ids[text_key]

        if not panel.visible:
            self._set_canvas_text(text_key, "")
            self._hide_sprite(unit_key)
            self._hide_sprite(char_key)
            return

        self._set_canvas_text(text_key, panel.value)
        self.canvas.coords(text_id, start_x, y)
        self.canvas.itemconfig(text_id, anchor="w")

        bbox = self.canvas.bbox(text_id)
        if not bbox:
            self._hide_sprite(unit_key)
            self._hide_sprite(char_key)
            return

        x0, y0, x1, y1 = bbox
        cy = (y0 + y1) // 2
        x = x1 + gap

        if panel.unit_file:
            w = self._place_aux_sprite(unit_key, panel.unit_file, x, cy, "w")
            x += w + gap
        else:
            self._hide_sprite(unit_key)
        if panel.char_file:
            self._place_aux_sprite(char_key, panel.char_file, x, cy, "w")
        else:
            self._hide_sprite(char_key)

    def _layout_aux_side(self, side: str, panel: AuxPanel) -> None:
        cache_key = (
            panel.visible, panel.value, panel.unit_file, panel.char_file,
        )
        if self._aux_cache.get(side) == cache_key:
            return
        self._aux_cache[side] = cache_key
        text_key = f"aux_{side}"
        unit_key = f"aux_{side}_unit"
        char_key = f"aux_{side}_char"
        gap = self._s(L.AUX_ICON_GAP)

        if not panel.visible:
            self._set_canvas_text(text_key, "")
            self._hide_sprite(unit_key)
            self._hide_sprite(char_key)
            return

        self._set_canvas_text(text_key, panel.value)
        text_id = self._text_ids[text_key]
        bbox = self.canvas.bbox(text_id)
        if not bbox:
            self._hide_sprite(unit_key)
            self._hide_sprite(char_key)
            return

        text_w = bbox[2] - bbox[0]
        unit_w = self._aux_sprite_width(panel.unit_file)
        char_w = self._aux_sprite_width(panel.char_file)
        total = text_w
        if panel.unit_file:
            total += gap + unit_w
        if panel.char_file:
            total += gap + char_w

        right_x = L.AUX_LEFT_RIGHT if side == "left" else L.SEC_RIGHT[0]
        start_x = self._s(right_x) - total
        self._layout_aux_row(
            text_key, unit_key, char_key, panel,
            start_x, self._s(L.AUX_ROW_Y),
        )

    def _update_aux_displays(self, m) -> None:
        left, right = build_aux_panels(m)
        self._layout_aux_side("left", left)
        self._layout_aux_side("right", right)

    def _place_main_unit_sprite(self, fname: str) -> None:
        layout = L.main_value_layout()
        ux, uy, uw, uh = layout["units"]
        cx = ux + uw // 2
        cy = uy + uh // 2
        photo = self.sprites.main_unit_sprite(
            fname, self.scale, max_w=self._s(uw), max_h=self._s(uh),
        )
        if photo:
            self._show_sprite("main_unit", photo, self._s(cx), self._s(cy), anchor="center")

    def _update_unit_sprites(self, kind: str, display_unit: str) -> None:
        unit_key = (kind, display_unit)
        if unit_key == self._last_unit_key:
            return
        self._last_unit_key = unit_key
        self._clear_unit_sprites()
        fname = main_unit_filename(kind, display_unit)
        if fname:
            self._place_main_unit_sprite(fname)

    def _draw_mode_buttons(self) -> None:
        self._mode_btn_ids = [gid for gid, _ in MODE_CYCLE_GROUPS]

    def _place_mode_button_bg(self, gid: str, rx: int, ry: int, rw: int, rh: int, active: bool) -> None:
        color = "buttons_active" if active else "buttons"
        radius = self._s(L.MODE_BTN_RADIUS)
        photo = self.sprites.rounded_button(color, rw, rh, radius)
        if photo:
            self.canvas.create_image(
                rx, ry, anchor="nw", image=photo,
                tags=("mode_btn", f"mode_bg_{gid}"),
            )

    def apply_view_mode(self, *, mini: bool, resize: bool = True) -> None:
        self._mini_mode = mini
        state = "hidden" if mini else "normal"
        for tag in ("save_slot_bg", "save_slot", "graph", "hit_main_save"):
            self.canvas.itemconfigure(tag, state=state)
        if resize:
            logical = L.dm40_main_height(mini=mini)
            self.resize_to_logical_height(logical)
        else:
            self.refresh_mode_buttons(self.app.mode_state)
        self._raise_visual_layers()
        self.raise_click_layer()

    def resize_to_logical_height(self, logical_h: int) -> None:
        self._logical_h = logical_h
        w = int(L.SCREEN_W * self.scale)
        h = int(logical_h * self.scale)
        self.configure(width=w, height=h)
        self.canvas.configure(width=w, height=h)
        self.refresh_mode_buttons(self.app.mode_state)

    def refresh_mode_buttons(self, mode_state) -> None:
        s = self.scale
        active = mode_state.active_group
        slots = L.mode_button_slots(mini=self._mini_mode)
        self.canvas.delete("mode_btn")
        for (gid, _opts), (x, y, w, h) in zip(MODE_CYCLE_GROUPS, slots):
            rx, ry, rw, rh = self._s(x), self._s(y), self._s(w), self._s(h)
            self._place_mode_button_bg(gid, rx, ry, rw, rh, gid == active)
            photo = self.sprites.mode_button(mode_state.current_cmd_key(gid), s, max_w=rw - 4, max_h=rh - 4)
            if photo:
                self.canvas.create_image(
                    rx + rw // 2, ry + rh // 2, image=photo,
                    tags=("mode_btn", f"mode_img_{gid}"),
                )
        self._rebind_mode_hotspots(slots)
        self.raise_click_layer()

    def _rebind_mode_hotspots(self, slots: list[tuple[int, int, int, int]]) -> None:
        dbg = self._debug_hotspots
        for gid, _ in MODE_CYCLE_GROUPS:
            self.canvas.delete(f"mode_hit_{gid}")
        for (gid, _opts), (x, y, w, h) in zip(MODE_CYCLE_GROUPS, slots):
            bind_clickable(
                self.canvas, self._s(x), self._s(y), self._s(w), self._s(h),
                lambda g=gid: self.app.cycle_mode(g),
                tag=f"mode_hit_{gid}",
                debug=dbg, debug_color="#208040",
            )

    def _bind_hotspots(self) -> None:
        dbg = self._debug_hotspots
        rx, ry, rw, rh = L.RANGE_HIT
        bind_clickable(
            self.canvas, self._s(rx), self._s(ry), self._s(rw), self._s(rh),
            self.app.show_range_screen, tag="hit_range",
            debug=dbg, debug_color="#2060c0",
        )
        hx, hy, hw, hh = L.HOLD_HIT
        bind_clickable(
            self.canvas, self._s(hx), self._s(hy), self._s(hw), self._s(hh),
            self._toggle_hold, tag="hit_hold",
            debug=dbg, debug_color="#c06020",
        )
        sx, sy, sw, sh = L.SETTINGS_HIT
        bind_clickable(
            self.canvas, self._s(sx), self._s(sy), self._s(sw), self._s(sh),
            self.app.show_settings_screen, tag="hit_settings",
            debug=dbg, debug_color="#8060c0",
        )

        self._rebind_mode_hotspots(L.mode_button_slots(mini=self._mini_mode))
        self._bind_main_value_save()
        self.raise_click_layer()

    def _cancel_long_press(self) -> None:
        if self._long_press_after is not None:
            self.app.root.after_cancel(self._long_press_after)
            self._long_press_after = None

    def _refresh_save_slots(self) -> None:
        gap = self._s(L.SAVE_UNIT_GAP)
        for i, (sx, sy, sw, sh) in enumerate(L.save_slot_slots()):
            reading = self._save_slots.slots[i]
            text_key = f"save_{i}"
            unit_key = f"save_{i}_unit"
            cy = self._s(sy + sh // 2)
            active = self._save_slots.last_index == i and reading.text

            if not reading.text:
                self._set_canvas_text(text_key, "")
                self.canvas.coords(text_key, 0, 0)
                self._hide_sprite(unit_key)
                continue

            color = rgb_hex("orange_main") if active else rgb_hex("text_primary")
            self.canvas.itemconfig(self._text_ids[text_key], fill=color)
            self._set_canvas_text(text_key, reading.text)
            self.canvas.coords(self._text_ids[text_key], self._s(sx + 2), cy)
            self.canvas.itemconfig(self._text_ids[text_key], anchor="w")

            bbox = self.canvas.bbox(self._text_ids[text_key])
            if not bbox:
                self._hide_sprite(unit_key)
                continue
            sprite_fname = save_unit_sprite_filename(reading.unit_file, active=active)
            if sprite_fname:
                photo = self.sprites.save_area_sprite(
                    sprite_fname, self.scale, max_h=self._s(L.SAVE_UNIT_MAX_H),
                )
                if photo:
                    self._show_sprite(unit_key, photo, bbox[2] + gap, cy, anchor="w")
                else:
                    self._hide_sprite(unit_key)
            else:
                self._hide_sprite(unit_key)

    def _on_main_save_click(self) -> None:
        if self._bt_off_display or self._last_display_measurement is None:
            return
        m, _rng = self._last_display_measurement
        text, unit_file = format_save_reading(m)
        self._save_slots.save(text, unit_file)
        self._refresh_save_slots()
        self.raise_click_layer()

    def _on_main_long_press(self) -> None:
        self._long_press_fired = True
        self._long_press_after = None
        self._save_slots.clear_all()
        self._refresh_save_slots()
        self.raise_click_layer()

    def _bind_main_value_save(self) -> None:
        layout = L.main_value_layout()
        rx, ry, rw, rh = layout["digits"]
        x, y, w, h = self._s(rx), self._s(ry), self._s(rw), self._s(rh)
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill="", outline="",
            tags=("hit_main_save", CLICK_HOTSPOT_TAG),
        )

        def on_press(_event) -> None:
            self._long_press_fired = False
            self._cancel_long_press()
            self._long_press_after = self.app.root.after(
                L.SAVE_LONG_PRESS_MS, self._on_main_long_press,
            )

        def on_release(_event) -> None:
            self._cancel_long_press()
            if not self._long_press_fired:
                self._on_main_save_click()

        self.canvas.tag_bind("hit_main_save", "<ButtonPress-1>", on_press)
        self.canvas.tag_bind("hit_main_save", "<ButtonRelease-1>", on_release)

    def refresh_all(self) -> None:
        """Rebuild all translatable text (called on language change)."""
        self.refresh_mode_buttons(self.app.mode_state)
        self._graph.refresh_rel_text()
        if self._bt_off_display:
            self._layout_main_value(t("main.bt_off"))
        self.raise_click_layer()

    def release_hold_freeze(self) -> None:
        """Release display freeze (e.g. after MODE → RUN on the device)."""
        self._display_frozen = False

    def _render_measurement(self, m, rng_label: str) -> None:
        """Render measurement on display (main digits, aux, units, HV)."""
        main_text = combined_main_value_str(
            m.kind, m.value_str, m.decimals,
            m.sec_val, m.third_val,
            overload=m.overload,
        )
        self._layout_main_value(main_text, m.decimals)
        self._update_hv_warning(is_high_voltage_warning(m))
        self._update_aux_displays(m)
        self._update_unit_sprites(m.kind, m.display_unit)
        label = rng_label or m.range or "AUTO+"
        if label != self._last_range_label:
            self._set_range_display(label)
        self._draw_display_debug_regions()

    def _update_device_status(self, m) -> None:
        self._set_hold_display(m.hold)
        self._set_lock_display(m.screen_locked)
        self._set_battery_display(m.battery_bars, m.charging)

    def _toggle_hold(self) -> None:
        if self._last_hold:
            self.app.ble.send_command(COMMANDS["RUN"])
            self._display_frozen = False
            self._set_hold_display(False)
        else:
            self.app.ble.send_command(COMMANDS["HOLD"])
            self._display_frozen = True
            self._set_hold_display(True)

    def update_measurement(self, m, rng_label: str, trace_key: int = 0) -> None:
        if self._bt_off_display:
            return

        was_hold = self._last_hold

        if m.hold:
            self._update_device_status(m)
            if not was_hold:
                self._display_frozen = True
                if self._last_display_measurement is not None:
                    self._render_measurement(*self._last_display_measurement)
            return

        self._display_frozen = False
        self._last_display_measurement = (m, rng_label)
        self._render_measurement(m, rng_label)
        if not self._mini_mode:
            self._graph.push_measurement(m, trace_key)
        self._update_device_status(m)

