"""Format numbers on the display – reserved sign column (Consolas)."""

from __future__ import annotations


def format_signed(
    value_str: str,
    decimals: int = 2,
    *,
    int_digits: int | None = None,
) -> str:
    """Return number with fixed sign column: space or ``-`` (text does not shift)."""
    if value_str in ("OL", "---", ""):
        return value_str
    try:
        value = float(value_str)
    except (TypeError, ValueError):
        return value_str

    sign = "-" if value < 0 else " "
    body = f"{abs(value):.{decimals}f}"
    if int_digits is not None and decimals > 0:
        int_part, _, frac = body.partition(".")
        body = f"{int_part.zfill(int_digits)}.{frac}"
    elif int_digits is not None:
        body = f"{abs(value):.0f}".zfill(int_digits)

    return sign + body


def split_main_value(value_str: str, decimals: int) -> tuple[str, str, str]:
    """Split main value into sign, body, and display mode.

    Returns:
        (sign, body, mode) where mode is ``numeric``, ``ol``, or ``text``.
    """
    if value_str == "OL":
        return (" ", "OL", "ol")
    if value_str in ("---", ""):
        return (" ", value_str or "---", "text")
    if value_str == format_signed(value_str, decimals) and value_str in ("OL",):
        return (" ", "OL", "ol")

    try:
        float(value_str)
    except (TypeError, ValueError):
        return (" ", value_str, "text")

    full = format_signed(value_str, decimals)
    if full.startswith("-"):
        return ("-", full[1:], "numeric")
    if full.startswith(" "):
        return (" ", full[1:], "numeric")
    return (" ", full, "numeric")


def format_measurement_main(kind: str, value_str: str, decimals: int, *, overload: bool) -> str:
    if overload:
        return "OL"
    return format_signed(value_str, decimals)


def combined_main_value_str(
    kind: str,
    value_str: str,
    decimals: int,
    dc_str: str,
    ac_str: str,
    *,
    overload: bool,
) -> str:
    """Main display for VDC+AC / ADC+AC – larger absolute component (AC or DC)."""
    if overload:
        return "OL"
    if kind not in ("VDC+AC", "ADC+AC"):
        return format_signed(value_str, decimals)

    try:
        dc = float(dc_str) if dc_str and dc_str != "OL" else None
        ac = float(ac_str) if ac_str and ac_str != "OL" else None
    except ValueError:
        return format_signed(value_str, decimals)

    if dc is None and ac is None:
        return format_signed(value_str, decimals)
    if dc is None:
        return format_signed(ac_str, decimals)
    if ac is None:
        return format_signed(dc_str, decimals)
    if abs(ac) >= abs(dc):
        return format_signed(ac_str, decimals)
    return format_signed(dc_str, decimals)
