"""Pozice prvků hlavní obrazovky (referenční 480×320 px).

Velikost okna = SCREEN_W × SCREEN_H × ``window_scale`` v settings.json
(+ rámeček Windows mimo obsah canvasu).
"""

SCREEN_W = 480
SCREEN_H = 300
TOP_BAR_H = 35
TOP_BAR_BG_Y = 0

# Horní lišta – pozice textu (anchor „w“, y při kreslení = [1] + 10 v main_screen.py)
RANGE_IMG = (5, 6)
HOLD_IMG = (100, 6)

# Klikací oblasti top baru – (x, y, w, h); při posunu HOLD_IMG se HOLD_HIT posune automaticky
_TOP_HIT_X = 4
_TOP_HIT_Y = 4
_TOP_HIT_H = TOP_BAR_H - _TOP_HIT_Y
_TOP_HIT_GAP = 4          # mezera mezi RANGE a HOLD zónou (bez překryvu)
_HOLD_HIT_PAD_LEFT = 6    # o kolik px vlevo od HOLD textu začíná HOLD klik
HOLD_HIT_W = 88           # šířka HOLD klikací zóny

HOLD_HIT_X = HOLD_IMG[0] - _HOLD_HIT_PAD_LEFT
RANGE_HIT = (_TOP_HIT_X, _TOP_HIT_Y, HOLD_HIT_X - _TOP_HIT_GAP - _TOP_HIT_X, _TOP_HIT_H)
HOLD_HIT = (HOLD_HIT_X, _TOP_HIT_Y, HOLD_HIT_W, _TOP_HIT_H)

# Pravý cluster top baru (zleva doprava: SETTINGS → LOCK → BLE → BATT) – doladění zde
TOP_BAR_ICON_Y = 10
TOP_BAR_ICON_H = 16
TOP_BAR_ICON_GAP = 18
TOP_BAR_SETTINGS_W = 27
TOP_BAR_LOCK_W = 27
TOP_BAR_BT_W = 19
TOP_BAR_BATTERY_W = 34
TOP_BAR_RIGHT_MARGIN = 5

_TOP_CLUSTER_W = (
    TOP_BAR_SETTINGS_W + TOP_BAR_ICON_GAP
    + TOP_BAR_LOCK_W + TOP_BAR_ICON_GAP
    + TOP_BAR_BT_W + TOP_BAR_ICON_GAP
    + TOP_BAR_BATTERY_W
)
TOP_BAR_SETTINGS_X = SCREEN_W - TOP_BAR_RIGHT_MARGIN - _TOP_CLUSTER_W
TOP_BAR_LOCK_X = TOP_BAR_SETTINGS_X + TOP_BAR_SETTINGS_W + TOP_BAR_ICON_GAP
TOP_BAR_BT_X = TOP_BAR_LOCK_X + TOP_BAR_LOCK_W + TOP_BAR_ICON_GAP
TOP_BAR_BATT_X = TOP_BAR_BT_X + TOP_BAR_BT_W + TOP_BAR_ICON_GAP

_SETTINGS_HIT_PAD = 4
SETTINGS_HIT = (
    TOP_BAR_SETTINGS_X - _SETTINGS_HIT_PAD,
    _TOP_HIT_Y,
    TOP_BAR_SETTINGS_W + 2 * _SETTINGS_HIT_PAD,
    _TOP_HIT_H,
)

SETTINGS_IMG = (TOP_BAR_SETTINGS_X, TOP_BAR_ICON_Y)
LOCK_IMG = (TOP_BAR_LOCK_X, TOP_BAR_ICON_Y)
BT_IMG = (TOP_BAR_BT_X, TOP_BAR_ICON_Y)
BATTERY_IMG = (TOP_BAR_BATT_X, TOP_BAR_ICON_Y)

# Horní AUX1 a AUX2 displeje – duty, Hz, AC/DC složky, …
AUX_ROW_Y = 48
SEC_LEFT = (55, AUX_ROW_Y)       # levý okraj zóny aux1
AUX_LEFT_RIGHT = 220             # pravý okraj aux1 – text zarovnaný doprava (jako aux2)
SEC_RIGHT = (390, AUX_ROW_Y)     # pravý okraj aux2
AUX_ICON_GAP = 1
AUX_ICON_MAX_H = 15
SEC_FONT = 17                    # Výška textu AUX1 a AUX2 displeje

# --- Hlavní řádek číslic (mezi aux displeji a grafem) ---
MAIN_VALUE_ROW_CY = 89           # vertikální střed řádku (od vrchu okna), center Y
MAIN_VALUE_ROW_H = 55
MAIN_VALUE_FONT = 55
MAIN_BT_OFF_FONT = 18            # „Turn ON Bluetooth“ – musí se vejít na šířku řádku
MAIN_SIGN_W = 22                 # červená oblast – sloupec „ “ / „-“
MAIN_DIGITS_W = 250              # zelená oblast – číslice / OL

# Okraje a mezery mezi debug oblastmi
MAIN_HV_LEFT_MARGIN = 8          # fialová (HV varování) od levého okraje okna
MAIN_HV_WARN_W = 28              # šířka fialové oblasti (0 = vypnuto varování)
MAIN_HV_SIGN_GAP = 70            # mezera fialová → červená (sign)
MAIN_DIGITS_UNIT_GAP = 0         # mezera zelená (číslice) → žlutá (jednotky). 8 default
MAIN_UNIT_W = 113                # přirozená šířka PNG v images/main_unit/
MAIN_UNIT_H = 68                 # přirozená výška PNG v images/main_unit/
MAIN_UNIT_COL_W = 91             # žlutá oblast – sprite se škáluje do COL_W × ROW_H
MAIN_UNIT_WINDOW_RIGHT_MARGIN = 10 # žlutá oblast od pravého okraje okna
MAIN_UNIT_MAX_H = max(MAIN_VALUE_ROW_H, MAIN_UNIT_H)

# Zpětná kompatibilita
MAIN_UNIT_RIGHT_GAP = MAIN_DIGITS_UNIT_GAP
MAIN_VALUE_LEFT = MAIN_HV_LEFT_MARGIN
MAIN_VALUE = (MAIN_VALUE_LEFT, MAIN_VALUE_ROW_CY)


def main_value_layout() -> dict[str, tuple[int, int, int, int]]:
    """(x, y, w, h) oblastí hlavního řádku – pro vykreslení a debug."""
    row_y = MAIN_VALUE_ROW_CY - MAIN_VALUE_ROW_H // 2
    units_x = SCREEN_W - MAIN_UNIT_WINDOW_RIGHT_MARGIN - MAIN_UNIT_COL_W
    digits_x = units_x - MAIN_DIGITS_UNIT_GAP - MAIN_DIGITS_W
    sign_x = digits_x - MAIN_SIGN_W
    hv_x = MAIN_HV_LEFT_MARGIN
    row_w = (units_x + MAIN_UNIT_COL_W) - hv_x
    return {
        "row": (hv_x, row_y, row_w, MAIN_VALUE_ROW_H),
        "hv_warn": (hv_x, row_y, MAIN_HV_WARN_W, MAIN_VALUE_ROW_H),
        "sign": (hv_x + MAIN_HV_WARN_W + MAIN_HV_SIGN_GAP, row_y, MAIN_SIGN_W, MAIN_VALUE_ROW_H),
        "digits": (digits_x, row_y, MAIN_DIGITS_W, MAIN_VALUE_ROW_H),
        "units": (units_x, row_y, MAIN_UNIT_COL_W, MAIN_VALUE_ROW_H),
    }


def aux_debug_layout() -> dict[str, tuple[int, int, int, int]]:
    """Debug obdélníky aux1 / aux2."""
    aux_y = AUX_ROW_Y - 8
    aux_h = 20
    return {
        "aux_left": (SEC_LEFT[0], aux_y, AUX_LEFT_RIGHT - SEC_LEFT[0], aux_h),
        "aux_right": (AUX_LEFT_RIGHT, aux_y, SEC_RIGHT[0] - AUX_LEFT_RIGHT, aux_h),
    }

# Save area – 5 slotů pod hlavními číslicemi (klik na číslice = uložit, dlouhý stisk = vymazat)
# Mezery SAVE_GAP_* = barva background; pozadí slotů = save_area (vykresluje se po slotech)
SAVE_SLOT_COUNT = 5
SAVE_SLOT_GAP = 4
SAVE_SLOT_MARGIN = 0
SAVE_GAP_TOP = 10              # mezera background nad sloty (pod hlavními číslicemi)
SAVE_GAP_BOTTOM = 4            # mezera background pod sloty (nad grafem)
SAVE_ROW_H = 24
SAVE_SLOT_RADIUS = 3           # zaoblení rohů save slotů (px při scale 1.0)
_MAIN_ROW_BOTTOM = MAIN_VALUE_ROW_CY + MAIN_VALUE_ROW_H // 2
SAVE_ROW_Y = _MAIN_ROW_BOTTOM + SAVE_GAP_TOP
SAVE_ROW_CY = SAVE_ROW_Y + SAVE_ROW_H // 2
SAVE_FONT = 12
SAVE_UNIT_MAX_H = 12
SAVE_UNIT_GAP = 2
SAVE_LONG_PRESS_MS = 600

# MODE řada (6× ~78 px) – Y od spodního okraje obrazovky
MODE_BTN_COUNT = 6
MODE_BTN_H = 34
MODE_BTN_GAP = 3
MODE_BTN_MARGIN = 5
MODE_BTN_RADIUS = 6  # zaoblení rohů MODE tlačítek (px při scale 1.0)
MODE_BTN_BOTTOM_MARGIN = 8  # mezera MODE řady od spodního okraje canvasu (ne Windows chrome)
MODE_BTN_Y = SCREEN_H - MODE_BTN_BOTTOM_MARGIN - MODE_BTN_H

# Mini app – jen top bar, aux, hlavní číslice a MODE řada
MINI_GAP_BEFORE_MODE = 10
_MAIN_ROW_BOTTOM = MAIN_VALUE_ROW_CY + MAIN_VALUE_ROW_H // 2
MINI_MODE_BTN_Y = _MAIN_ROW_BOTTOM + MINI_GAP_BEFORE_MODE
MINI_SCREEN_H = MINI_MODE_BTN_Y + MODE_BTN_H + MODE_BTN_BOTTOM_MARGIN

# RAW konzole pod hlavní obrazovkou (referenční px při scale 1.0)
RAW_CONSOLE_H = 200           # výška konzole
RAW_CONSOLE_FONT = 10         # velikost textu v konzoli
RAW_CONSOLE_MAX_LINES = 200   # maximální počet řádků v konzoli
RAW_CONSOLE_POLL_MS = 230     # poll TX/RX: max 1 řádek / interval; zbytek se zahodí

# Oblast grafu pod save sloty (SAVE_GAP_BOTTOM = černá mezera nad grafem)
_GRAPH_TOP = SAVE_ROW_Y + SAVE_ROW_H + SAVE_GAP_BOTTOM
GRAPH_AREA = (0, _GRAPH_TOP, SCREEN_W, MODE_BTN_Y - 7 - _GRAPH_TOP)

# Graf – plot na celou šířku mínus pravý sloupec; škála vepsaná do plotu vlevo
GRAPH_SIDEBAR_W = 72
GRAPH_FONT = 11
GRAPH_RADIUS = 3           # zaoblení pozadí celého grafu (px při scale 1.0)
GRAPH_SCALE_PAD_X = 4
GRAPH_SCALE_LABEL_MARGIN = 4  # mezera za škálovým textem před střední grid čárou
GRAPH_GRID_FRACS = (0.25, 0.5, 0.75)
GRAPH_REL_BTN_W = 56
GRAPH_REL_BTN_H = 28
GRAPH_REL_RADIUS = 4
GRAPH_LONG_PRESS_MS = 600
GRAPH_SAMPLE_MAX = 512


def graph_layout() -> dict[str, tuple[int, int, int, int]]:
    """(x, y, w, h) pro plot, sidebar a REL tlačítko (referenční px)."""
    gx, gy, gw, gh = GRAPH_AREA
    plot_w = gw - GRAPH_SIDEBAR_W
    sx = gx + plot_w
    rel_x = sx + (GRAPH_SIDEBAR_W - GRAPH_REL_BTN_W) // 2
    rel_y = gy + (gh - GRAPH_REL_BTN_H) // 2
    return {
        "plot": (gx, gy, plot_w, gh),
        "sidebar": (sx, gy, GRAPH_SIDEBAR_W, gh),
        "rel_btn": (rel_x, rel_y, GRAPH_REL_BTN_W, GRAPH_REL_BTN_H),
    }


def save_slot_slots() -> list[tuple[int, int, int, int]]:
    """(x, y, w, h) pro každý save slot zleva doprava."""
    usable = SCREEN_W - 2 * SAVE_SLOT_MARGIN - (SAVE_SLOT_COUNT - 1) * SAVE_SLOT_GAP 
    w = (usable + SAVE_SLOT_COUNT - 1) // SAVE_SLOT_COUNT # maximalizace šířky slotů, původně bylo w = usable // SAVE_SLOT_COUNT
    slots = []
    x = SAVE_SLOT_MARGIN
    for _ in range(SAVE_SLOT_COUNT):
        slots.append((x, SAVE_ROW_Y, w, SAVE_ROW_H))
        x += w + SAVE_SLOT_GAP
    return slots


def mode_button_slots(*, mini: bool = False) -> list[tuple[int, int, int, int]]:
    """(x, y, w, h) pro každou skupinu MODE."""
    y = MINI_MODE_BTN_Y if mini else MODE_BTN_Y
    usable = SCREEN_W - 2 * MODE_BTN_MARGIN - (MODE_BTN_COUNT - 1) * MODE_BTN_GAP
    w = (usable + MODE_BTN_COUNT - 1) // MODE_BTN_COUNT # maximalizace šířky slotů, původně bylo w = usable // MODE_BTN_COUNT
    slots = []
    x = MODE_BTN_MARGIN
    for _ in range(MODE_BTN_COUNT):
        slots.append((x, y, w, MODE_BTN_H))
        x += w + MODE_BTN_GAP
    return slots


def dm40_main_height(*, mini: bool) -> int:
    return MINI_SCREEN_H if mini else SCREEN_H
