"""Layout SETTINGS obrazovky (referenční 480×{SCREEN_H} px)."""

from gui import layout as L
from gui.range_layout import RANGE_BACK_IMG, range_back_hit

SETTINGS_ROW_MARGIN = 5
SETTINGS_ROW_H = 44
SETTINGS_ROW_GAP = 5
SETTINGS_LABEL_FONT = 13
SETTINGS_STATE_FONT = 12
SETTINGS_SWITCH_MAX_H = 19
SETTINGS_SWITCH_GAP = 8
SETTINGS_TITLE_FONT = 14
SETTINGS_TITLE_Y = 16
SETTINGS_BACK_IMG = RANGE_BACK_IMG

SETTING_ROWS: list[tuple[str, str]] = [
    ("mini_app", "Mini app"),
    ("always_on_top", "Always on top"),
    ("raw_console", "RAW data console"),
]


def settings_back_hit() -> tuple[int, int, int, int]:
    return range_back_hit()


def settings_row_slots() -> list[tuple[int, int, int, int]]:
    """(x, y, w, h) pro každý řádek nastavení."""
    x = SETTINGS_ROW_MARGIN
    w = L.SCREEN_W - 2 * SETTINGS_ROW_MARGIN
    y = L.TOP_BAR_H + SETTINGS_ROW_MARGIN
    slots = []
    for _ in SETTING_ROWS:
        slots.append((x, y, w, SETTINGS_ROW_H))
        y += SETTINGS_ROW_H + SETTINGS_ROW_GAP
    return slots
