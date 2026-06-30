"""Layout Connect (cold run) obrazovky."""

from gui.layout import MODE_BTN_GAP, MODE_BTN_H, MODE_BTN_MARGIN, MODE_BTN_Y, SCREEN_W, TOP_BAR_H

SETUP_TITLE_FONT = 14
SETUP_TITLE_Y = 16
SETUP_HINT_Y = 52
SETUP_HINT_FONT = 12
SETUP_STATUS_Y = 78
SETUP_STATUS_FONT = 12
SETUP_LIST_MARGIN = 5
SETUP_LIST_TOP = 96
SETUP_ROW_H = 38
SETUP_ROW_GAP = 4
SETUP_ROW_FONT = 12
SETUP_ROW_PAD_LEFT = 10
SETUP_BTN_COUNT = 2
SETUP_BTN_LABELS = ("Search", "Connect")


def setup_list_bottom() -> int:
    return MODE_BTN_Y - 8


def setup_button_slots() -> list[tuple[int, int, int, int]]:
    """(x, y, w, h) pro Search a Connect – stejná řada jako MODE tlačítka."""
    y = MODE_BTN_Y
    usable = SCREEN_W - 2 * MODE_BTN_MARGIN - (SETUP_BTN_COUNT - 1) * MODE_BTN_GAP
    w = usable // SETUP_BTN_COUNT
    slots = []
    x = MODE_BTN_MARGIN
    for _ in range(SETUP_BTN_COUNT):
        slots.append((x, y, w, MODE_BTN_H))
        x += w + MODE_BTN_GAP
    return slots
