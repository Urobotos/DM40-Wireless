"""SETTINGS screen – canvas GUI styled like the RANGE menu."""

from __future__ import annotations

import os
import tkinter as tk

from core.config import SCREEN_HEIGHT, SCREEN_WIDTH
from core.i18n import t, get_i18n, i18n_dir
from gui import layout as L
from gui import settings_layout as SL
from gui.assets import bind_clickable, raise_click_hotspots
from gui.settings import save_settings
from gui.sprites import SpriteCache
from gui.theme import rgb_hex


class SettingsScreen(tk.Frame):
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

        self._title_id: int | None = None
        self._back_sprite_id: int | None = None
        self._lang_popup: tk.Toplevel | None = None
        self._lang_popup_dismiss_bind: str | None = None

        self._draw_top_bar()
        self._bind_back()

    def _s(self, v: float) -> int:
        return int(v * self.scale)

    def raise_click_layer(self) -> None:
        raise_click_hotspots(self.canvas)

    def _draw_top_bar(self) -> None:
        self.canvas.create_rectangle(
            0, 0, self._s(L.SCREEN_W), self._s(L.TOP_BAR_H),
            fill=rgb_hex("top_bar_background"), outline="", tags="settings_chrome",
        )
        font = ("sans-serif", self._s(SL.SETTINGS_TITLE_FONT), "bold")
        self._title_id = self.canvas.create_text(
            self._s(L.SCREEN_W // 2), self._s(SL.SETTINGS_TITLE_Y), text=t("settings.title"),
            fill=rgb_hex("text_primary"), anchor="center", font=font, tags="settings_chrome",
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
                self._s(SL.SETTINGS_BACK_IMG[0]), self._s(SL.SETTINGS_BACK_IMG[1]),
                anchor="nw", image=photo, tags="settings_chrome",
            )

    def _bind_back(self) -> None:
        bx, by, bw, bh = SL.settings_back_hit()
        bind_clickable(
            self.canvas, self._s(bx), self._s(by), self._s(bw), self._s(bh),
            self.app.show_main_screen, tag="settings_hit_back",
        )

    def rebuild(self) -> None:
        self._close_lang_popup()
        if self._title_id is not None:
            self.canvas.itemconfig(self._title_id, text=t("settings.title"))
        self.canvas.delete("settings_row")
        label_font = ("sans-serif", self._s(SL.SETTINGS_LABEL_FONT), "normal")
        state_font = ("sans-serif", self._s(SL.SETTINGS_STATE_FONT), "bold")

        for (key, label), (x, y, w, h) in zip(SL.setting_rows(), SL.settings_row_slots()):
            if key == "language":
                self._place_language_row(x, y, w, h, key, label, label_font, state_font)
            else:
                enabled = bool(self.app.settings.get(key, False))
                self._place_row(x, y, w, h, key, label, enabled, label_font, state_font)

        self.raise_click_layer()

    def _row_frame(self, key: str, x: int, y: int, w: int, h: int, label: str, label_font: tuple) -> tuple[int, int, int, int, int]:
        rx, ry, rw, rh = self._s(x), self._s(y), self._s(w), self._s(h)
        self.canvas.create_rectangle(
            rx, ry, rx + rw, ry + rh,
            fill=rgb_hex("range_buttons"), outline="",
            tags=("settings_row", f"settings_bg_{key}"),
        )
        cy = ry + rh // 2
        pad_l = self._s(SL.SETTINGS_ROW_MARGIN)
        self.canvas.create_text(
            rx + pad_l, cy, text=label,
            fill=rgb_hex("text_primary"), anchor="w", font=label_font,
            tags=("settings_row", f"settings_lbl_{key}"),
        )
        return rx, ry, rw, rh, cy

    def _place_row(
        self,
        x: int, y: int, w: int, h: int,
        key: str, label: str, enabled: bool,
        label_font: tuple, state_font: tuple,
    ) -> None:
        rx, ry, rw, rh, cy = self._row_frame(key, x, y, w, h, label, label_font)

        switch = self.sprites.settings_sprite(
            "switch_on.png" if enabled else "switch_off.png",
            self.scale,
            max_h=self._s(SL.SETTINGS_SWITCH_MAX_H),
        )
        state_text = t("settings.state_on") if enabled else t("settings.state_off")
        state_color = rgb_hex("buttons_active") if enabled else rgb_hex("text_secondary")
        gap = self._s(SL.SETTINGS_SWITCH_GAP)
        pad_r = self._s(SL.SETTINGS_ROW_MARGIN)

        if switch:
            switch_x = rx + rw - pad_r - switch.width()
            self.canvas.create_image(
                switch_x, cy, anchor="w", image=switch,
                tags=("settings_row", f"settings_sw_{key}"),
            )
            state_x = switch_x - gap
        else:
            state_x = rx + rw - pad_r

        self.canvas.create_text(
            state_x, cy, text=state_text,
            fill=state_color, anchor="e", font=state_font,
            tags=("settings_row", f"settings_state_{key}"),
        )
        bind_clickable(
            self.canvas, rx, ry, rw, rh,
            lambda k=key: self._toggle(k), tag=f"settings_hit_{key}",
        )

    def _toggle(self, key: str) -> None:
        self.app.settings[key] = not bool(self.app.settings.get(key, False))
        save_settings(self.app.settings)
        self.app.apply_settings()
        self.rebuild()

    def _close_lang_popup(self) -> None:
        if self._lang_popup is not None:
            try:
                self._lang_popup.destroy()
            except tk.TclError:
                pass
            self._lang_popup = None
        if self._lang_popup_dismiss_bind:
            self.app.root.unbind("<Button-1>", self._lang_popup_dismiss_bind)
            self._lang_popup_dismiss_bind = None

    def _open_i18n_folder(self) -> None:
        """Open i18n/ in Explorer; refresh language list when app regains focus."""
        self._close_lang_popup()
        folder = i18n_dir()
        folder.mkdir(parents=True, exist_ok=True)
        os.startfile(str(folder))

        def on_focus(_event=None) -> None:
            self.rebuild()
            self.app.root.unbind("<FocusIn>")

        self.app.root.bind("<FocusIn>", on_focus, add="+")

    def _select_language(self, lang_code: str) -> None:
        current = (self.app.settings.get("language") or "").strip() or "en-US"
        self._close_lang_popup()
        if lang_code == current:
            return
        self.app.reload_language(lang_code)

    def _toggle_lang_popup(self, rx: int, ry: int, rw: int, rh: int) -> None:
        if self._lang_popup is not None:
            self._close_lang_popup()
            return
        self._show_lang_popup(rx, ry, rw, rh)

    def _show_lang_popup(self, rx: int, ry: int, rw: int, rh: int) -> None:
        languages = get_i18n().available_languages()
        if not languages:
            return

        current = (self.app.settings.get("language") or "").strip() or "en-US"
        pad = self._s(SL.LANGUAGE_POPUP_PAD)
        item_h = self._s(SL.LANGUAGE_ITEM_H)
        item_gap = self._s(SL.LANGUAGE_ITEM_GAP)
        popup_w = max(rw, self._s(180))
        popup_h = pad * 2 + len(languages) * item_h + max(0, len(languages) - 1) * item_gap

        popup = tk.Toplevel(self.app.root)
        popup.overrideredirect(True)
        popup.configure(bg=rgb_hex("buttons_active"))
        popup.attributes("-topmost", True)

        screen_x = self.canvas.winfo_rootx() + rx + rw - popup_w
        screen_y = self.canvas.winfo_rooty() + ry + rh + 2
        popup.geometry(f"{popup_w}x{popup_h}+{screen_x}+{screen_y}")

        inner = tk.Frame(popup, bg=rgb_hex("background"), padx=pad, pady=pad)
        inner.pack(fill="both", expand=True)

        label_font = ("sans-serif", self._s(SL.SETTINGS_LABEL_FONT), "normal")

        for lang_code, display in languages.items():
            active = lang_code == current
            bg = rgb_hex("buttons_active") if active else rgb_hex("range_buttons")
            fg = rgb_hex("text_primary")
            row = tk.Frame(inner, bg=bg, height=item_h)
            row.pack(fill="x", pady=(0, item_gap))
            row.pack_propagate(False)

            lbl = tk.Label(
                row, text=display, bg=bg, fg=fg, anchor="w",
                font=label_font, padx=self._s(SL.SETTINGS_ROW_MARGIN),
            )
            lbl.pack(fill="both", expand=True)

            def on_pick(_event=None, code=lang_code):
                self._select_language(code)

            for widget in (row, lbl):
                widget.bind("<Button-1>", on_pick)

        self._lang_popup = popup

        def dismiss(event: tk.Event) -> None:
            if self._lang_popup is None:
                return
            try:
                wx, wy = event.x_root, event.y_root
                px, py = self._lang_popup.winfo_rootx(), self._lang_popup.winfo_rooty()
                pw, ph = self._lang_popup.winfo_width(), self._lang_popup.winfo_height()
                inside_popup = px <= wx <= px + pw and py <= wy <= py + ph
                inside_selector = (
                    self.canvas.winfo_rootx() + rx <= wx <= self.canvas.winfo_rootx() + rx + rw
                    and self.canvas.winfo_rooty() + ry <= wy <= self.canvas.winfo_rooty() + ry + rh
                )
                if not inside_popup and not inside_selector:
                    self._close_lang_popup()
            except tk.TclError:
                self._close_lang_popup()

        self._lang_popup_dismiss_bind = self.app.root.bind("<Button-1>", dismiss, add="+")

    def _place_language_row(
        self, x: int, y: int, w: int, h: int, key: str, label: str,
        label_font: tuple, state_font: tuple,
    ) -> None:
        rx, ry, rw, rh, cy = self._row_frame(key, x, y, w, h, label, label_font)
        pad_l = self._s(SL.SETTINGS_ROW_MARGIN)
        pad_r = self._s(SL.SETTINGS_ROW_MARGIN)

        lang_icon = self.sprites.settings_sprite(
            "lang_icon.png", self.scale, max_h=self._s(SL.LANGUAGE_LANG_ICON_MAX_H),
        )
        lbl_id = self.canvas.find_withtag(f"settings_lbl_{key}")
        if lang_icon and lbl_id:
            bbox = self.canvas.bbox(lbl_id[0])
            if bbox:
                icon_x = bbox[2] + self._s(SL.LANGUAGE_LANG_ICON_GAP)
                self.canvas.create_image(
                    icon_x, cy, anchor="w", image=lang_icon,
                    tags=("settings_row", f"settings_lang_icon_{key}"),
                )

        folder_icon = self.sprites.settings_sprite(
            "folder.png", self.scale, max_h=self._s(SL.LANGUAGE_FOLDER_ICON_MAX_H),
        )
        folder_pad = self._s(4)
        if folder_icon:
            folder_x = rx + rw - pad_r - folder_icon.width()
            folder_y = cy - folder_icon.height() // 2
            self.canvas.create_image(
                folder_x, folder_y, anchor="nw", image=folder_icon,
                tags=("settings_row", f"settings_folder_{key}"),
            )
            bind_clickable(
                self.canvas,
                folder_x, folder_y,
                folder_icon.width(), folder_icon.height(),
                self._open_i18n_folder,
                tag=f"settings_folder_hit_{key}",
            )
            selector_right = folder_x - folder_pad
        else:
            selector_right = rx + rw - pad_r

        lang_code = (self.app.settings.get("language") or "").strip() or "en-US"
        display = get_i18n().available_languages().get(lang_code, lang_code)
        selector_left = rx + self._s(120)
        selector_top = ry + self._s(6)
        selector_bottom = ry + rh - self._s(6)
        selector_h = selector_bottom - selector_top
        selector_w = max(self._s(80), selector_right - selector_left)

        self.canvas.create_rectangle(
            selector_left, selector_top,
            selector_left + selector_w, selector_bottom,
            fill=rgb_hex("buttons"), outline="",
            tags=("settings_row", f"settings_selector_bg_{key}"),
        )
        self.canvas.create_text(
            selector_left + selector_w // 2, cy,
            text=f"{display}  ▼", anchor="center", font=state_font,
            fill=rgb_hex("text_primary"),
            tags=("settings_row", f"settings_selector_txt_{key}"),
        )
        bind_clickable(
            self.canvas,
            selector_left, selector_top, selector_w, selector_h,
            lambda: self._toggle_lang_popup(selector_left, selector_top, selector_w, selector_h),
            tag=f"settings_selector_hit_{key}",
        )
