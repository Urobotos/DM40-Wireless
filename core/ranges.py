"""Ranges (RANGE) by active measurement mode."""

from .protocol_constants import (
    FLAG_INFO,
    MODEL_CURRENT_RANGE_LABELS,
    MODEL_OHM_RANGE_LABELS,
    MODEL_VOLTAGE_RANGE_LABELS,
    VOLTAGE_RANGE_SLOT,
)

RANGE_CAPABLE_KINDS = (
    "VDC", "VAC", "VDC+AC",
    "ADC", "AAC", "ADC+AC",
    "RES", "RES_ONLINE",
)

CURRENT_RANGE_SLOT = {
    0x01: 0, 0x09: 1, 0x11: 2, 0x19: 3, 0x21: 4, 0x29: 5,
    0x41: 0, 0x49: 1, 0x51: 2, 0x59: 3, 0x61: 4, 0x69: 5,
    0x81: 0, 0x89: 1, 0x91: 2, 0x99: 3, 0xA1: 4, 0xA9: 5,
}

OHM_RANGE_SLOT = {
    0x02: 0, 0x0A: 1, 0x12: 2, 0x1A: 3, 0x22: 4, 0x2A: 5,
    0x42: 0, 0x4A: 1, 0x52: 2, 0x5A: 3, 0x62: 4, 0x6A: 5,
}

_CMD_KEY_TO_KIND = {
    "VDC": "VDC",
    "VAC": "VAC",
    "VDC+VAC": "VDC+AC",
    "ADC": "ADC",
    "AAC": "AAC",
    "ADC+AAC": "ADC+AC",
    "OHM": "RES",
    "OHM_ONLINE": "RES_ONLINE",
}


def make_range_cmd(flag: int) -> bytes:
    payload = [0xAF, 0x05, 0x03, 0x06, 0x01, flag]
    payload.append((-sum(payload)) & 0xFF)
    return bytes(payload)


def range_display_label(flag: int, model_name: str) -> str:
    try:
        _kind, rng = FLAG_INFO[flag]
    except KeyError:
        return ""
    if rng.startswith("AUTO"):
        return rng
    if flag in VOLTAGE_RANGE_SLOT:
        return MODEL_VOLTAGE_RANGE_LABELS[model_name][VOLTAGE_RANGE_SLOT[flag]]
    if flag in CURRENT_RANGE_SLOT:
        return MODEL_CURRENT_RANGE_LABELS[model_name][CURRENT_RANGE_SLOT[flag]]
    if flag in OHM_RANGE_SLOT:
        return MODEL_OHM_RANGE_LABELS[model_name][OHM_RANGE_SLOT[flag]]
    return rng


def ranges_for_kind(kind: str, model_name: str) -> list[tuple[str, int]]:
    if kind not in RANGE_CAPABLE_KINDS:
        return []
    items: list[tuple[str, int]] = []
    for flag in sorted(FLAG_INFO):
        k, rng = FLAG_INFO[flag]
        if k != kind:
            continue
        if rng == "AUTO+" and k in ("RES", "RES_ONLINE"):
            continue
        items.append((range_display_label(flag, model_name), flag))
    return items


def kind_from_mode_cmd_key(cmd_key: str) -> str | None:
    return _CMD_KEY_TO_KIND.get(cmd_key)
