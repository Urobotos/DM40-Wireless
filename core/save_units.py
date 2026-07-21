"""Map display units to PNG files for save slots (images/save_area/)."""

from __future__ import annotations

from core.config import IMAGES_DIR

SAVE_AREA_DIR = IMAGES_DIR / "save_area"

SAVE_UNIT_FILES: dict[str, str] = {
    "V": "v.png",
    "mV": "m_v.png",
    "A": "a.png",
    "mA": "m_a.png",
    "uA": "u_a.png",
    "Ω": "ohm.png",
    "kΩ": "k_ohm.png",
    "KΩ": "k_ohm.png",
    "MΩ": "m_ohm.png",
    "nF": "n_f.png",
    "uF": "u_f.png",
    "mF": "m_f.png",
    "Hz": "hz.png",
    "kHz": "k_hz.png",
    "KHz": "k_hz.png",
    "MHz": "m_hz.png",
    "°C": "deg_c.png",
}


def save_unit_filename(kind: str, display_unit: str) -> str | None:
    """Base (orange) unit PNG for saving to a slot – without AC/DC symbols."""
    if kind == "TEMP":
        display_unit = "°C"
    if not display_unit:
        return None
    fname = SAVE_UNIT_FILES.get(display_unit)
    if fname and (SAVE_AREA_DIR / fname).is_file():
        return fname
    for key, val in SAVE_UNIT_FILES.items():
        if key.lower() == display_unit.lower() and (SAVE_AREA_DIR / val).is_file():
            return val
    return None


def save_unit_sprite_filename(base_fname: str | None, *, active: bool) -> str | None:
    """PNG for rendering – active slot: orange version, others: *_white.png."""
    if not base_fname:
        return None
    if active:
        return base_fname if (SAVE_AREA_DIR / base_fname).is_file() else None
    white = base_fname.replace(".png", "_white.png")
    return white if (SAVE_AREA_DIR / white).is_file() else None
