"""Settings screen layout (reference 480×{SCREEN_H} px)."""

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

LANGUAGE_ITEM_H = 24
LANGUAGE_ITEM_GAP = 2
LANGUAGE_POPUP_PAD = 4
LANGUAGE_FOLDER_ICON_MAX_H = 20
LANGUAGE_LANG_ICON_MAX_H = 18
LANGUAGE_LANG_ICON_GAP = 6
LANGUAGE_SELECTOR_PAD = 8

def setting_rows() -> list[tuple[str, str]]:
    """Return translated setting rows (key, label)."""
    from core.i18n import t
    return [
        ("mini_app", t("settings.label_mini_app")),
        ("always_on_top", t("settings.label_always_on_top")),
        ("raw_console", t("settings.label_raw_console")),
        ("language", t("settings.label_language")),
    ]


def settings_back_hit() -> tuple[int, int, int, int]:
    return range_back_hit()


def settings_row_slots() -> list[tuple[int, int, int, int]]:
    """(x, y, w, h) for each settings row."""
    rows = setting_rows()
    x = SETTINGS_ROW_MARGIN
    w = L.SCREEN_W - 2 * SETTINGS_ROW_MARGIN
    y = L.TOP_BAR_H + SETTINGS_ROW_MARGIN
    slots = []
    for _ in rows:
        slots.append((x, y, w, SETTINGS_ROW_H))
        y += SETTINGS_ROW_H + SETTINGS_ROW_GAP
    return slots
