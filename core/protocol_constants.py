"""DM40 BLE protocol – constants for parsing measurement frames."""

HEADER = b"\xdf\x05\x03\x09"
MODEL_PACKET_PREFIX = b"\xdf\x05\x03\x08\x14"
CMD_ID = b"\xaf\x05\x03\x08\x00\x41"

MODEL_TABLE = (("DM40A", 40000), ("DM40B", 50000), ("DM40C", 60000))

MODEL_VOLTAGE_RANGE_LABELS = {
    "DM40A": ("400mV", "4V", "40V", "400V", "1000V"),
    "DM40B": ("500mV", "5V", "50V", "500V", "1000V"),
    "DM40C": ("600mV", "6V", "60V", "600V", "1000V"),
}

MODEL_CURRENT_RANGE_LABELS = {
    "DM40A": ("400uA", "4mA", "40mA", "400mA", "4A", "10A"),
    "DM40B": ("500uA", "5mA", "50mA", "500mA", "5A", "10A"),
    "DM40C": ("600uA", "6mA", "60mA", "600mA", "6A", "10A"),
}

MODEL_OHM_RANGE_LABELS = {
    "DM40A": ("400Ω", "4kΩ", "40kΩ", "400kΩ", "4MΩ", "40MΩ"),
    "DM40B": ("500Ω", "5kΩ", "50kΩ", "500kΩ", "5MΩ", "50MΩ"),
    "DM40C": ("600Ω", "6kΩ", "60kΩ", "600kΩ", "6MΩ", "60MΩ"),
}

VOLTAGE_RANGE_SLOT = {
    0x00: 0, 0x08: 1, 0x10: 2, 0x18: 3, 0x20: 4,
    0x40: 0, 0x48: 1, 0x50: 2, 0x58: 3, 0x60: 4,
    0x80: 0, 0x88: 1, 0x90: 2, 0x98: 3, 0xA0: 4,
}

def range_screen_title(kind: str) -> str:
    """Return internationalized range screen title for the given measurement kind."""
    from core.i18n import t
    key = kind.replace("+", "_plus_")
    return t(f"range_titles.{key}")

# Keep RANGE_SCREEN_TITLES as backward-compatible default fallback
RANGE_SCREEN_TITLES = {
    "VDC": "Voltage Settings",
    "VAC": "Voltage Settings",
    "VDC+AC": "Voltage Settings",
    "ADC": "Current Settings",
    "AAC": "Current Settings",
    "ADC+AC": "Current Settings",
    "RES": "Resistor Settings",
    "RES_ONLINE": "Resistor Settings",
}

FLAG_INFO = {
    0x00: ("VDC", "600mV"),
    0x08: ("VDC", "6V"),
    0x10: ("VDC", "60V"),
    0x18: ("VDC", "600V"),
    0x20: ("VDC", "1000V"),
    0x28: ("VDC", "AUTO"),
    0x30: ("VDC", "AUTO+"),
    0x40: ("VAC", "600mV"),
    0x48: ("VAC", "6V"),
    0x50: ("VAC", "60V"),
    0x58: ("VAC", "600V"),
    0x60: ("VAC", "1000V"),
    0x68: ("VAC", "AUTO"),
    0x70: ("VAC", "AUTO+"),
    0x80: ("VDC+AC", "600mV"),
    0x88: ("VDC+AC", "6V"),
    0x90: ("VDC+AC", "60V"),
    0x98: ("VDC+AC", "600V"),
    0xA0: ("VDC+AC", "1000V"),
    0xA8: ("VDC+AC", "AUTO"),
    0xB0: ("VDC+AC", "AUTO+"),
    0x01: ("ADC", "600uA"),
    0x09: ("ADC", "6mA"),
    0x11: ("ADC", "60mA"),
    0x19: ("ADC", "600mA"),
    0x21: ("ADC", "6A"),
    0x29: ("ADC", "10A"),
    0x31: ("ADC", "AUTO"),
    0x39: ("ADC", "AUTO+"),
    0x41: ("AAC", "600uA"),
    0x49: ("AAC", "6mA"),
    0x51: ("AAC", "60mA"),
    0x59: ("AAC", "600mA"),
    0x61: ("AAC", "6A"),
    0x69: ("AAC", "10A"),
    0x71: ("AAC", "AUTO"),
    0x79: ("AAC", "AUTO+"),
    0x81: ("ADC+AC", "600uA"),
    0x89: ("ADC+AC", "6mA"),
    0x91: ("ADC+AC", "60mA"),
    0x99: ("ADC+AC", "600mA"),
    0xA1: ("ADC+AC", "6A"),
    0xA9: ("ADC+AC", "10A"),
    0xB1: ("ADC+AC", "AUTO"),
    0xB9: ("ADC+AC", "AUTO+"),
    0x02: ("RES", "600Ω"),
    0x0A: ("RES", "6kΩ"),
    0x12: ("RES", "60kΩ"),
    0x1A: ("RES", "600kΩ"),
    0x22: ("RES", "6MΩ"),
    0x2A: ("RES", "60MΩ"),
    0x32: ("RES", "AUTO"),
    0x42: ("RES_ONLINE", "600Ω"),
    0x4A: ("RES_ONLINE", "6kΩ"),
    0x52: ("RES_ONLINE", "60kΩ"),
    0x5A: ("RES_ONLINE", "600kΩ"),
    0x62: ("RES_ONLINE", "6MΩ"),
    0x6A: ("RES_ONLINE", "60MΩ"),
    0x72: ("RES_ONLINE", "AUTO"),
    0x03: ("CAP", "AUTO"),
    0x04: ("DIODE", "AUTO"),
    0x44: ("CONT", "AUTO"),
    0x05: ("FREQ", "AUTO"),
    0x45: ("TEMP", "AUTO"),
}

ALT_SCALE_MAP = {
    0x04: (0.6, "mV", 1e3, 2),
    0x08: (6.0, "V", 1.0, 4),
    0x18: (6.0, "V", 1.0, 4),
    0x16: (60.0, "V", 1.0, 3),
    0x14: (600.0, "V", 1.0, 2),
    0x12: (6000.0, "V", 1.0, 1),
}

AMP_SCALE_MAP = {
    0x04: (600e-6, "uA", 1e6, 2),
    0x02: (6000e-6, "uA", 1e6, 1),
    0x16: (60e-3, "mA", 1e3, 3),
    0x14: (600e-3, "mA", 1e3, 2),
    0x28: (6.0, "A", 1.0, 4),
    0x26: (60.0, "A", 1.0, 3),
}

RES_SCALE_MAP = {
    0x04: (600.0, "Ω", 1.0, 2),
    0x02: (6000.0, "Ω", 1.0, 1),
    0x18: (6000.0, "kΩ", 0.001, 4),
    0x16: (60000.0, "kΩ", 0.001, 3),
    0x14: (600000.0, "kΩ", 0.001, 2),
    0x28: (6e6, "MΩ", 1e-6, 4),
    0x26: (6e7, "MΩ", 1e-6, 3),
}

# CONT (continuity) – probe short often uses scale 0x84 (132), not a normal RES range
CONT_SCALE_MAP = {
    0x84: (600.0, "Ω", 1.0, 2),
    0x04: (600.0, "Ω", 1.0, 2),
    0x02: (6000.0, "Ω", 1.0, 1),
}

FREQ_SCALE_MAP = {
    0x06: (60.0, "Hz", 1.0, 3),
    0x04: (600.0, "Hz", 1.0, 2),
    0x02: (6_000.0, "Hz", 1.0, 1),
    0x18: (6_000.0, "kHz", 1e-3, 4),
    0x16: (60_000.0, "kHz", 1e-3, 3),
    0x14: (600_000.0, "kHz", 1e-3, 2),
}

CAP_SCALE_MAP = {
    0x06: (6e-9, "nF", 1e9, 3),
    0x04: (60e-9, "nF", 1e9, 2),
    0x02: (600e-9, "nF", 1e9, 1),
    0x16: (6e-6, "uF", 1e6, 3),
    0x14: (60e-6, "uF", 1e6, 2),
    0x12: (600e-6, "uF", 1e6, 1),
    0x26: (6e-3, "mF", 1e3, 3),
    0x24: (60e-3, "mF", 1e3, 2),
}

MODE_SLOT_MAP = {
    "VDC": ("M1",),
    "VAC": ("M1", "DUTY", "FREQ"),
    "VDC+AC": ("M1", "DC", "AC"),
    "ADC": ("M1", "DUTY"),
    "AAC": ("M1", "DUTY", "FREQ"),
    "ADC+AC": ("M1", "DC", "AC"),
    "RES": ("M1",),
    "RES_ONLINE": ("M1",),
    "CAP": ("M1",),
    "CONT": ("M1",),
    "DIODE": ("M1", "RES"),
    "FREQ": ("FREQ", "DUTY"),
    "TEMP": ("TC", "TF", "TI"),
}
