"""Formátování hodnot pro graf (škála, MIN, MAX)."""

UNIT_TO_BASE: dict[str, float] = {
    "mV": 1e-3,
    "V": 1.0,
    "uA": 1e-6,
    "mA": 1e-3,
    "A": 1.0,
    "Ω": 1.0,
    "kΩ": 1e3,
    "MΩ": 1e6,
    "Hz": 1.0,
    "kHz": 1e3,
    "nF": 1e-9,
    "uF": 1e-6,
    "mF": 1e-3,
    "°C": 1.0,
    "°F": 1.0,
    "%": 1.0,
}


def axis_mul_for_unit(unit: str) -> float:
    return UNIT_TO_BASE.get(unit, 1.0)


def format_graph_value(norm_value: float, unit: str, decimals: int) -> str:
    """Kompaktní zápis jako na DM40 (např. ``-0.0435V``, ``0.000MΩ``)."""
    mul = axis_mul_for_unit(unit)
    return f"{norm_value / mul:.{decimals}f}{unit}"


def format_graph_scale_label(norm_value: float, unit: str, decimals: int) -> str:
    """Škála vlevo v grafu – sloupec znaménka pro zarovnání top/mid/bot."""
    mul = axis_mul_for_unit(unit)
    disp = norm_value / mul
    sign = "-" if disp < 0 else " "
    return f"{sign}{abs(disp):.{decimals}f}{unit}"
