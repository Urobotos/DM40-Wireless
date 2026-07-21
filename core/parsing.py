"""Parse DM40 measurement NOTIFY frames."""

from .protocol_constants import (
    ALT_SCALE_MAP,
    AMP_SCALE_MAP,
    CAP_SCALE_MAP,
    CONT_SCALE_MAP,
    FLAG_INFO,
    FREQ_SCALE_MAP,
    HEADER,
    MODE_SLOT_MAP,
    MODEL_PACKET_PREFIX,
    MODEL_TABLE,
    RES_SCALE_MAP,
)
from .ranges import range_display_label

# Measurement frame: DF 05 03 09 [0B] flag status … scale@9 … M3@10 M2@12 M1@14 (see sniffing.txt CONT TEST)
_MEAS_SUBTYPE = 0x0B
_FLAG_BYTE = 5
_STATUS_BYTE = 6
_SCALE_M1, _SCALE_M2, _SCALE_M3 = 9, 8, 7
_M3_LO, _M3_HI = 10, 11
_M2_LO, _M2_HI = 12, 13
_M1_LO, _M1_HI = 14, 15


def _uses_measurement_layout(data: bytes) -> bool:
    return len(data) >= 17 and data[4] == _MEAS_SUBTYPE


def _scale_bytes(data: bytes) -> tuple[int, int, int]:
    if _uses_measurement_layout(data):
        return data[_SCALE_M1], data[_SCALE_M2], data[_SCALE_M3]
    if len(data) >= 16:
        return data[-8], data[-9], data[-10]
    return 0, 0, 0


def _slot_counts(data: bytes) -> tuple[int, int, int]:
    if len(data) < 16:
        return 0, 0, 0
    m3 = (data[_M3_HI] << 8) | data[_M3_LO]
    m2 = (data[_M2_HI] << 8) | data[_M2_LO]
    m1 = (data[_M1_HI] << 8) | data[_M1_LO]
    return m1, m2, m3


class ModelInfo:
    __slots__ = ("model_name", "device_counts")

    def __init__(self, model_name="DM40A", device_counts=40000):
        self.model_name = model_name
        self.device_counts = device_counts


MODEL = ModelInfo()


class Measurement:
    __slots__ = (
        "raw", "kind", "range", "display_unit", "value_str", "norm_value",
        "vertical_pad", "decimals", "sec_val", "sec_unit", "third_val",
        "third_unit", "overload", "crc_str",
        "battery_bars", "charging", "screen_locked", "hold",
    )

    def __init__(self):
        self.raw = ""
        self.kind = "---"
        self.range = ""
        self.display_unit = ""
        self.value_str = "---"
        self.norm_value = None
        self.vertical_pad = 0.0
        self.decimals = 2
        self.sec_val = ""
        self.sec_unit = ""
        self.third_val = ""
        self.third_unit = ""
        self.overload = False
        self.crc_str = ""
        self.battery_bars = 0
        self.charging = False
        self.screen_locked = False
        self.hold = False


def apply_model(model_name: str, device_counts: int) -> None:
    MODEL.model_name = model_name
    MODEL.device_counts = device_counts


def guess_model_from_ble_name(name: str) -> bool:
    upper = (name or "").upper()
    for model_name, device_counts in MODEL_TABLE:
        if model_name in upper:
            apply_model(model_name, device_counts)
            return True
    return False


def try_parse_model_packet(data: bytes) -> bool:
    if len(data) < 10 or data[:5] != MODEL_PACKET_PREFIX:
        return False
    idx = data[9] - 0x41
    if 0 <= idx < len(MODEL_TABLE):
        apply_model(*MODEL_TABLE[idx])
    return True


def range_name_for_flag(flag_byte: int) -> str:
    return range_display_label(flag_byte, MODEL.model_name)


def _scale_info(kind: str, slot: str, scale_flag: int) -> tuple | None:
    if slot == "FREQ":
        return FREQ_SCALE_MAP.get(scale_flag)
    if slot not in ("M1", "DC", "AC"):
        if slot == "TC" and kind == "TEMP":
            return (6000.0, "°C", 1.0, 1)
        if slot == "RES" and kind == "DIODE":
            return (6000.0, "Ω", 1.0, 1)
        return None
    if kind.startswith("V") or kind == "DIODE":
        return ALT_SCALE_MAP.get(scale_flag)
    if kind.startswith("A"):
        return AMP_SCALE_MAP.get(scale_flag)
    if kind == "CONT":
        return CONT_SCALE_MAP.get(scale_flag) or RES_SCALE_MAP.get(scale_flag)
    if kind in ("RES", "RES_ONLINE"):
        return RES_SCALE_MAP.get(scale_flag)
    if kind == "CAP":
        return CAP_SCALE_MAP.get(scale_flag)
    return None


def resolve_slot_scale(slot: str, kind: str, sign_flag: int):
    scale_flag = sign_flag & 0xFE
    info = _scale_info(kind, slot, scale_flag)
    if info is None:
        return None
    factor = MODEL.device_counts / 60000.0
    fs_base, unit, mul, dec = info
    return fs_base * factor, unit, mul, dec


def parse_device_status(data: bytes) -> tuple:
    status = data[_STATUS_BYTE]
    return (
        status & 0x07,
        (status & 0x08) != 0,
        (status & 0x40) != 0,
        (status & 0x80) != 0,
    )


def process_slot(slot_type: str, counts: int, sign_flag: int, kind: str):
    ol = counts == 0xFFFF
    if resolved := resolve_slot_scale(slot_type, kind, sign_flag):
        full_scale, disp_unit, disp_mul, decimals = resolved
        if ol:
            return "OL", disp_unit
        sign = -1 if (sign_flag & 1) else 1
        val_disp = counts * (full_scale / MODEL.device_counts) * disp_mul * sign
        return "%.*f" % (decimals, val_disp), disp_unit
    if slot_type == "DUTY":
        if ol:
            return "OL", "%"
        sign = -1 if (sign_flag & 1) else 1
        # ADC: -00.00 % (2 decimal places, scale 0.01); AAC/VAC: 0.0 % (scale 0.1)
        scale = 0.01 if kind == "ADC" else 0.1
        decimals = 2 if kind == "ADC" else 1
        val_disp = sign * counts * scale
        return "%.*f" % (decimals, val_disp), "%"
    if slot_type in ("TF", "TI"):
        val_str = "OL" if ol else "%.1f" % (counts * 0.1)
        return val_str, "°F" if slot_type == "TF" else "°C INT"
    return "", ""


def range_label_from_packet(data: bytes, parsed_range: str) -> str:
    if len(data) >= 16 and data.startswith(HEADER):
        return range_name_for_flag(data[_FLAG_BYTE]) or parsed_range
    return parsed_range


def parse_measurement_for_ui(data: bytes) -> Measurement:
    m = Measurement()
    m.raw = data.hex(" ").upper()
    m.crc_str = "PASS" if (sum(data) & 0xFF) == 0 else "FAIL"
    if len(data) < 16 or not data.startswith(HEADER):
        return m

    bars, charging, locked, hold = parse_device_status(data)
    m.battery_bars, m.charging, m.screen_locked, m.hold = bars, charging, locked, hold

    m1, m2, m3 = _slot_counts(data)

    kind, rng_name = FLAG_INFO[data[_FLAG_BYTE]]
    m.kind, m.range, m.overload = kind, rng_name, (m1 == 0xFFFF)
    slots = MODE_SLOT_MAP[kind]
    s0, s1, s2 = _scale_bytes(data)

    if m.overload:
        m.value_str = "OL"

    if not (res1 := resolve_slot_scale(slots[0], kind, s0)):
        if kind == "CONT":
            m.display_unit = "Ω"
        return m

    fs1, unit1, mul1, dec1 = res1
    m.display_unit, m.decimals = unit1, dec1
    eff_counts = MODEL.device_counts / 10 if kind == "CAP" else MODEL.device_counts
    m.vertical_pad = 50 * (fs1 / eff_counts)

    if not m.overload:
        sign = -1 if (s0 & 0x01) else 1
        m.norm_value = sign * m1 * (fs1 / eff_counts)
        m.value_str = "%.*f" % (dec1, m.norm_value * mul1)

    if not rng_name.startswith("AUTO"):
        m.range = range_name_for_flag(data[_FLAG_BYTE])

    if len(slots) > 1:
        m.sec_val, m.sec_unit = process_slot(slots[1], m2, s1, kind)
    if len(slots) > 2:
        m.third_val, m.third_unit = process_slot(slots[2], m3, s2, kind)

    return m
