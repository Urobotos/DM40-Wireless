"""Layout RANGE obrazovky (referenční 480×{SCREEN_H} px)."""

from gui.layout import SCREEN_W, TOP_BAR_H

RANGE_BTN_MARGIN = 5
RANGE_BTN_GAP = 5
RANGE_BTN_H = 38
RANGE_BTN_COLS = 3
RANGE_BTN_FONT = 13
RANGE_TITLE_FONT = 14
RANGE_SEL_ICON_MAX_H = 30
RANGE_SEL_ICON_GAP = 3
RANGE_BTN_PAD_LEFT = 8  # zarovnání ikony + textu vlevo (stejné ve všech řádcích)
RANGE_BACK_IMG = (8, 8)
RANGE_BACK_HIT_PAD = 4
RANGE_TITLE_Y = 16

VOLTAGE_KINDS = ("VDC", "VAC", "VDC+AC")
CURRENT_KINDS = ("ADC", "AAC", "ADC+AC")
OHM_KINDS = ("RES", "RES_ONLINE")
SUBTYPE_KINDS = VOLTAGE_KINDS + CURRENT_KINDS + OHM_KINDS

SUBTYPE_ROW_LABELS: dict[str, list[tuple[str, str]]] = {
    "voltage": [("AC", "VAC"), ("DC", "VDC"), ("AC+DC", "VDC+VAC")],
    "current": [("AC", "AAC"), ("DC", "ADC"), ("AC+DC", "ADC+AAC")],
    "resistor": [("Off line", "OHM"), ("On line", "OHM_ONLINE")],
}


def range_back_hit() -> tuple[int, int, int, int]:
    w = 48
    return (
        RANGE_BACK_HIT_PAD,
        RANGE_BACK_HIT_PAD,
        w,
        TOP_BAR_H - RANGE_BACK_HIT_PAD,
    )


def _button_width() -> int:
    usable = SCREEN_W - 2 * RANGE_BTN_MARGIN - (RANGE_BTN_COLS - 1) * RANGE_BTN_GAP
    return usable // RANGE_BTN_COLS


def range_button_slots(count: int, *, start_y: int) -> list[tuple[int, int, int, int]]:
    """(x, y, w, h) pro ``count`` range tlačítek v mřížce 3 sloupce."""
    bw = _button_width()
    row_h = RANGE_BTN_H + RANGE_BTN_GAP
    slots = []
    for i in range(count):
        row, col = divmod(i, RANGE_BTN_COLS)
        x = RANGE_BTN_MARGIN + col * (bw + RANGE_BTN_GAP)
        y = start_y + row * row_h
        slots.append((x, y, bw, RANGE_BTN_H))
    return slots


def subtype_row_y(range_count: int, *, start_y: int) -> int:
    rows = (range_count + RANGE_BTN_COLS - 1) // RANGE_BTN_COLS
    return start_y + rows * (RANGE_BTN_H + RANGE_BTN_GAP)


def subtype_group(kind: str | None) -> str | None:
    if kind in VOLTAGE_KINDS:
        return "voltage"
    if kind in CURRENT_KINDS:
        return "current"
    if kind in OHM_KINDS:
        return "resistor"
    return None
