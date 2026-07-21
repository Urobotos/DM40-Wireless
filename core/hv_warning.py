"""High voltage warning – VDC / VAC / VDC+AC."""

from __future__ import annotations

from core.parsing import Measurement

VOLTAGE_KINDS = frozenset({"VDC", "VAC", "VDC+AC"})

# Dry environment – typical multimeter / safety practice (not from DM40 manual)
HV_THRESHOLD_AC_V = 50.0
HV_THRESHOLD_DC_V = 120.0

_VOLTAGE_TO_VOLTS = {
    "V": 1.0,
    "mV": 0.001,
}

HV_WARNING_IMAGE = "high_voltage_warning.png"


def _abs_volts(value_str: str, unit: str) -> float | None:
    if not value_str or value_str == "OL":
        return None
    scale = _VOLTAGE_TO_VOLTS.get(unit)
    if scale is None:
        return None
    try:
        return abs(float(value_str)) * scale
    except ValueError:
        return None


def is_high_voltage_warning(m: Measurement) -> bool:
    """True if measured voltage exceeds the threshold for the given mode."""
    if m.kind not in VOLTAGE_KINDS or m.overload:
        return False

    if m.kind == "VDC":
        v = _abs_volts(m.value_str, m.display_unit)
        return v is not None and v >= HV_THRESHOLD_DC_V

    if m.kind == "VAC":
        v = _abs_volts(m.value_str, m.display_unit)
        return v is not None and v >= HV_THRESHOLD_AC_V

    # VDC+AC – DC component (sec) ≥ 120 V, AC component (third) ≥ 50 V
    dc_v = _abs_volts(m.sec_val, m.sec_unit or "V")
    ac_v = _abs_volts(m.third_val, m.third_unit or "V")
    dc_warn = dc_v is not None and dc_v >= HV_THRESHOLD_DC_V
    ac_warn = ac_v is not None and ac_v >= HV_THRESHOLD_AC_V
    return dc_warn or ac_warn
