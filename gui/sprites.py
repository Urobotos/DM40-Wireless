"""Načítání a mapování PNG spriteů."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk

from core.config import IMAGES_DIR
from gui.theme import RGB_COLORS

MODE_BTN_DIR = IMAGES_DIR / "MODE_buttons"
RANGE_MENU_DIR = IMAGES_DIR / "range_menu_screen"
SETTINGS_DIR = IMAGES_DIR / "settings"
DISPLAY_UNIT_DIR = IMAGES_DIR / "aux_unit"
MAIN_UNIT_DIR = IMAGES_DIR / "main_unit"
from core.save_units import SAVE_AREA_DIR

TOP_BAR_DIR = IMAGES_DIR / "top_bar"

MAIN_UNIT_NATURAL_W = 133
MAIN_UNIT_NATURAL_H = 68

CMD_KEY_TO_MODE_IMAGE: dict[str, str] = {
    "VDC": "VDC.png",
    "VAC": "VAC.png",
    "VDC+VAC": "VDC+VAC.png",
    "ADC": "ADC.png",
    "AAC": "AAC.png",
    "ADC+AAC": "ADC+AAC.png",
    "OHM": "OHM.png",
    "OHM_ONLINE": "OHM_ONLINE.png",
    "CAP": "CAP.png",
    "DIODE": "DIODE_and_CONT.png",
    "CONT": "DIODE_and_CONT.png",
    "HZ": "HZ.png",
    "TEMP": "TEMP.png",
}

KIND_CHAR_ICON: dict[str, str] = {
    "VDC": "char_dc.png",
    "VAC": "char_ac.png",
    "VDC+AC": "char_ac+dc.png",
    "ADC": "char_dc.png",
    "AAC": "char_ac.png",
    "ADC+AC": "char_ac+dc.png",
}

KIND_SPECIAL_UNITS: dict[str, tuple[str, str]] = {
    "DIODE": ("diode.png", "V.png"),
    "CONT": ("cont.png", "ohm.png"),
}

RANGE_TOP_IMAGES: dict[str, str] = {
    "AUTO+": "auto+.png",
    "AUTO": "auto.png",
}

UNIT_TO_FILE: dict[str, str] = {
    "V": "V.png",
    "mV": "mV.png",
    "A": "A.png",
    "mA": "mA.png",
    "uA": "uA.png",
    "Ω": "ohm.png",
    "KΩ": "Kohm.png",
    "MΩ": "Mohm.png",
    "%": "percent.png",
    "Hz": "Hz.png",
    "KHz": "KHz.png",
    "MHz": "MHz.png",
    "nF": "nF.png",
    "uF": "uF.png",
    "mF": "mF.png",
    "°C": "degC.png",
    "°F": "degF.png",
}


def unit_icon_filename(unit: str) -> str | None:
    if not unit:
        return None
    if unit in UNIT_TO_FILE:
        return UNIT_TO_FILE[unit]
    for key, fname in UNIT_TO_FILE.items():
        if key.lower() == unit.lower():
            return fname
    return None


def aux_char_filename(name: str) -> str:
    """Horní AUX displeje – menší varianty char_*.png."""
    if name.endswith("_aux.png"):
        return name
    return name.replace(".png", "_aux.png")


# Hlavní displej – jeden PNG na režim + jednotku (images/main_unit/)
MAIN_KIND_PREFIX: dict[str, str] = {
    "VDC": "dc",
    "VAC": "ac",
    "VDC+AC": "ac_dc",
    "ADC": "dc",
    "AAC": "ac",
    "ADC+AC": "ac_dc",
}

MAIN_UNIT_SUFFIX: dict[str, str] = {
    "V": "v",
    "mV": "mv",
    "A": "a",
    "mA": "ma",
    "uA": "ua",
    "Ω": "ohm",
    "kΩ": "k_ohm",
    "MΩ": "m_ohm",
    "nF": "n_f",
    "uF": "u_f",
    "mF": "m_f",
    "Hz": "hz",
    "kHz": "khz",
    "MHz": "mhz",
    "°C": "deg_c",
    "°F": "deg_f",
}

MAIN_UNIT_STANDALONE: dict[str, str] = {
    "DIODE": "diode.png",
    "CONT": "cont.png",
}


def _main_unit_suffix(display_unit: str) -> str | None:
    if not display_unit:
        return None
    if display_unit in MAIN_UNIT_SUFFIX:
        return MAIN_UNIT_SUFFIX[display_unit]
    lower = display_unit.lower()
    for key, val in MAIN_UNIT_SUFFIX.items():
        if key.lower() == lower:
            return val
    return None


def main_unit_filename(kind: str, display_unit: str) -> str | None:
    """Soubor v ``images/main_unit/`` pro daný režim a jednotku měření."""
    if kind in MAIN_UNIT_STANDALONE:
        fname = MAIN_UNIT_STANDALONE[kind]
        return fname if (MAIN_UNIT_DIR / fname).is_file() else None

    suffix = _main_unit_suffix(display_unit)
    if not suffix:
        return None

    candidates: list[str] = []
    if prefix := MAIN_KIND_PREFIX.get(kind):
        candidates.append(f"{prefix}_{suffix}.png")
    candidates.append(f"{suffix}.png")

    for fname in candidates:
        if (MAIN_UNIT_DIR / fname).is_file():
            return fname
    return None


def aux_unit_icon_filename(unit: str) -> str | None:
    """Horní AUX displeje – menší varianty jednotek (Hz_aux.png, …)."""
    fname = unit_icon_filename(unit)
    if not fname:
        return None
    if fname.endswith("_aux.png"):
        return fname
    return fname.replace(".png", "_aux.png")


class SpriteCache:
    def __init__(self) -> None:
        self._cache: dict[tuple, tk.PhotoImage] = {}

    def load(
        self,
        path: Path,
        scale: float,
        *,
        max_width: int | None = None,
        max_height: int | None = None,
    ) -> tk.PhotoImage | None:
        if not path.is_file():
            return None
        key = (str(path), scale, max_width, max_height)
        if key in self._cache:
            return self._cache[key]
        try:
            from PIL import Image, ImageTk
        except ImportError:
            return None
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        if max_width or max_height:
            tw = max_width or w
            th = max_height or h
            ratio = min(tw / w, th / h)
            nw, nh = max(1, int(w * ratio)), max(1, int(h * ratio))
            img = img.resize((nw, nh), Image.Resampling.LANCZOS)
        elif scale != 1.0:
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale)), Image.Resampling.LANCZOS))
        photo = ImageTk.PhotoImage(img)
        self._cache[key] = photo
        return photo

    def rounded_button(
        self, color_name: str, width: int, height: int, radius: int,
    ) -> tk.PhotoImage | None:
        if width < 2 or height < 2:
            return None
        rgb = RGB_COLORS.get(color_name, RGB_COLORS["buttons"])
        r = max(1, min(radius, width // 2, height // 2))
        key = ("rounded_btn", color_name, width, height, r)
        if key in self._cache:
            return self._cache[key]
        try:
            from PIL import Image, ImageDraw, ImageTk
        except ImportError:
            return None
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=r, fill=(*rgb, 255))
        photo = ImageTk.PhotoImage(img)
        self._cache[key] = photo
        return photo

    def mode_button(self, cmd_key: str, scale: float, max_w: int, max_h: int) -> tk.PhotoImage | None:
        fname = CMD_KEY_TO_MODE_IMAGE.get(cmd_key)
        if not fname:
            return None
        return self.load(MODE_BTN_DIR / fname, scale, max_width=max_w, max_height=max_h)

    def top_bar(self, name: str, scale: float, max_w: int, max_h: int) -> tk.PhotoImage | None:
        return self.load(TOP_BAR_DIR / name, scale, max_width=max_w, max_height=max_h)

    def display_unit(self, fname: str, scale: float, max_h: int = 32) -> tk.PhotoImage | None:
        return self.load(DISPLAY_UNIT_DIR / fname, scale, max_height=max_h)

    def display_unit_aux(self, fname: str, scale: float, max_h: int = 12) -> tk.PhotoImage | None:
        """AUX sprite – preferuje *_aux.png, při absenci spadne na hlavní verzi."""
        path = DISPLAY_UNIT_DIR / fname
        if not path.is_file() and fname.endswith("_aux.png"):
            return self.display_unit(fname.replace("_aux.png", ".png"), scale, max_h=max_h)
        return self.display_unit(fname, scale, max_h=max_h)

    def main_unit_sprite(
        self, fname: str, scale: float, max_w: int, max_h: int,
    ) -> tk.PhotoImage | None:
        return self.load(MAIN_UNIT_DIR / fname, scale, max_width=max_w, max_height=max_h)

    def save_area_sprite(self, fname: str, scale: float, max_h: int = 12) -> tk.PhotoImage | None:
        return self.load(SAVE_AREA_DIR / fname, scale, max_height=max_h)

    def range_menu_sprite(
        self, fname: str, scale: float, *, max_w: int | None = None, max_h: int | None = None,
    ) -> tk.PhotoImage | None:
        return self.load(RANGE_MENU_DIR / fname, scale, max_width=max_w, max_height=max_h)

    def settings_sprite(
        self, fname: str, scale: float, *, max_w: int | None = None, max_h: int | None = None,
    ) -> tk.PhotoImage | None:
        return self.load(SETTINGS_DIR / fname, scale, max_width=max_w, max_height=max_h)

    def range_sprite(self, label: str, scale: float, max_w: int, max_h: int) -> tk.PhotoImage | None:
        fname = RANGE_TOP_IMAGES.get(label.strip())
        if not fname:
            return None
        return self.top_bar(fname, scale, max_w, max_h)

    def battery_sprite(self, bars: int, charging: bool, scale: float, max_w: int, max_h: int) -> tk.PhotoImage | None:
        if charging:
            return self.top_bar("battery_charging.png", scale, max_w, max_h)
        level = max(0, min(5, bars)) * 20
        return self.top_bar(f"battery_{level}perc.png", scale, max_w, max_h)
