"""RANGE obrazovka – canvas GUI podle DM40 multimetru."""

from __future__ import annotations

import tkinter as tk

from core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from core.controller import COMMANDS
from core.modes import KIND_TO_CMD
from core.parsing import MODEL
from core.protocol_constants import RANGE_SCREEN_TITLES
from core.ranges import RANGE_CAPABLE_KINDS, kind_from_mode_cmd_key, ranges_for_kind
from gui import layout as L
from gui import range_layout as RL
from gui.assets import bind_clickable, raise_click_hotspots
from gui.sprites import SpriteCache
from gui.theme import rgb_hex


class RangeScreen(tk.Frame):
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

        self._active_flag = 0
        self._title_id: int | None = None
        self._back_sprite_id: int | None = None

        self._draw_top_bar()
        self._bind_back()

    def _s(self, v: float) -> int:
        return int(v * self.scale)

    def raise_click_layer(self) -> None:
        raise_click_hotspots(self.canvas)

    def _draw_top_bar(self) -> None:
        self.canvas.create_rectangle(
            0, 0, self._s(L.SCREEN_W), self._s(L.TOP_BAR_H),
            fill=rgb_hex("top_bar_background"), outline="", tags="range_chrome",
        )
        font = ("sans-serif", self._s(RL.RANGE_TITLE_FONT), "bold")
        self._title_id = self.canvas.create_text(
            self._s(L.SCREEN_W // 2), self._s(RL.RANGE_TITLE_Y), text="Range",
            fill=rgb_hex("text_primary"), anchor="center", font=font, tags="range_chrome",
        )
        self._place_back_icon()

    def _place_back_icon(self) -> None:
        if self._back_sprite_id is not None:
            self.canvas.delete(self._back_sprite_id)
            self._back_sprite_id = None
        max_h = self._s(L.TOP_BAR_H - 12)
        photo = self.sprites.range_menu_sprite("back.png", self.scale, max_h=max_h)
        if photo:
            self._back_sprite_id = self.canvas.create_image(
                self._s(RL.RANGE_BACK_IMG[0]), self._s(RL.RANGE_BACK_IMG[1]),
                anchor="nw", image=photo, tags="range_chrome",
            )

    def _bind_back(self) -> None:
        bx, by, bw, bh = RL.range_back_hit()
        bind_clickable(
            self.canvas, self._s(bx), self._s(by), self._s(bw), self._s(bh),
            self.app.show_main_screen, tag="range_hit_back",
        )

    def rebuild_for_kind(self, kind: str | None, active_flag: int = 0) -> None:
        self._active_flag = active_flag
        self.canvas.delete("range_btn")
        self.canvas.delete("range_subtype")

        if not kind or kind not in RANGE_CAPABLE_KINDS:
            if self._title_id is not None:
                self.canvas.itemconfig(
                    self._title_id, text="Range — first select V / A / Ω mode",
                )
            self.raise_click_layer()
            return

        if self._title_id is not None:
            self.canvas.itemconfig(
                self._title_id, text=RANGE_SCREEN_TITLES.get(kind, f"Range — {kind}"),
            )

        items = ranges_for_kind(kind, MODEL.model_name)
        start_y = L.TOP_BAR_H + RL.RANGE_BTN_MARGIN
        font = ("sans-serif", self._s(RL.RANGE_BTN_FONT), "normal")

        for (label, flag), (x, y, w, h) in zip(items, RL.range_button_slots(len(items), start_y=start_y)):
            self._place_range_button(x, y, w, h, label, flag, flag == active_flag, font)

        group = RL.subtype_group(kind)
        if group:
            sy = RL.subtype_row_y(len(items), start_y=start_y)
            options = RL.SUBTYPE_ROW_LABELS[group]
            slots = RL.range_button_slots(len(options), start_y=sy)
            for (text, cmd_key), (x, y, w, h) in zip(options, slots):
                active = KIND_TO_CMD.get(kind) == cmd_key
                self._place_subtype_button(x, y, w, h, text, cmd_key, active, font)

        self.raise_click_layer()

    def _place_range_button(
        self, x: int, y: int, w: int, h: int, label: str, flag: int, active: bool, font: tuple,
    ) -> None:
        rx, ry, rw, rh = self._s(x), self._s(y), self._s(w), self._s(h)
        self.canvas.create_rectangle(
            rx, ry, rx + rw, ry + rh,
            fill=rgb_hex("range_buttons"), outline="", tags=("range_btn", f"range_bg_{flag}"),
        )
        icon_name = "btnsel1.png" if active else "btnsel0.png"
        icon = self.sprites.range_menu_sprite(
            icon_name, self.scale, max_h=self._s(RL.RANGE_SEL_ICON_MAX_H),
        )
        text_color = rgb_hex("buttons_active") if active else rgb_hex("text_primary")
        cy = ry + rh // 2
        pad_l = self._s(RL.RANGE_BTN_PAD_LEFT)
        if icon:
            gap = self._s(RL.RANGE_SEL_ICON_GAP)
            ix = rx + pad_l
            self.canvas.create_image(ix, cy, anchor="w", image=icon, tags=("range_btn", f"range_ico_{flag}"))
            self.canvas.create_text(
                ix + icon.width() + gap, cy, text=label,
                fill=text_color, anchor="w", font=font, tags=("range_btn", f"range_txt_{flag}"),
            )
        else:
            self.canvas.create_text(
                rx + pad_l, cy, text=label, fill=text_color, anchor="w", font=font,
                tags=("range_btn", f"range_txt_{flag}"),
            )
        bind_clickable(
            self.canvas, rx, ry, rw, rh,
            lambda f=flag: self._pick(f), tag=f"range_hit_{flag}",
        )

    def _place_subtype_button(
        self, x: int, y: int, w: int, h: int, text: str, cmd_key: str, active: bool, font: tuple,
    ) -> None:
        rx, ry, rw, rh = self._s(x), self._s(y), self._s(w), self._s(h)
        bg = "buttons_active" if active else "range_buttons"
        self.canvas.create_rectangle(
            rx, ry, rx + rw, ry + rh,
            fill=rgb_hex(bg), outline="", tags=("range_subtype", f"subtype_bg_{cmd_key}"),
        )
        self.canvas.create_text(
            rx + rw // 2, ry + rh // 2, text=text,
            fill=rgb_hex("text_primary"), anchor="center", font=font,
            tags=("range_subtype", f"subtype_txt_{cmd_key}"),
        )
        bind_clickable(
            self.canvas, rx, ry, rw, rh,
            lambda k=cmd_key: self._pick_subtype(k), tag=f"subtype_hit_{cmd_key}",
        )

    def _pick(self, flag: int) -> None:
        self.app.ble.send_range_flag(flag)
        self.app.show_main_screen()

    def _pick_subtype(self, cmd_key: str) -> None:
        self.app.ble.send_command(COMMANDS[cmd_key])
        kind = kind_from_mode_cmd_key(cmd_key)
        if kind:
            self.app.mode_state.last_kind = kind
            self.app.mode_state.sync_from_kind(kind)
            self.app.main_screen.refresh_mode_buttons(self.app.mode_state)
            self.rebuild_for_kind(kind, self._active_flag)
        self.raise_click_layer()
