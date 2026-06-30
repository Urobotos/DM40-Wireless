"""Horní úzké displeje (levý / pravý) podle režimu měření."""

from __future__ import annotations

from dataclasses import dataclass

from core.config import ADC_AUX_DUTY_ENABLED
from core.display_format import format_signed
from core.parsing import Measurement
from gui.sprites import aux_char_filename, aux_unit_icon_filename


@dataclass(frozen=True)
class AuxPanel:
    value: str = ""
    unit_file: str | None = None
    char_file: str | None = None

    @property
    def visible(self) -> bool:
        return bool(self.value)


def _unit_file(unit: str) -> str | None:
    if unit == "°C INT":
        unit = "°C"
    return aux_unit_icon_filename(unit)


def _fmt(val: str, decimals: int, *, int_digits: int | None = None) -> str:
    if not val:
        return ""
    if val == "OL":
        return "OL"
    return format_signed(val, decimals, int_digits=int_digits)


def _combined_aux(
    ac_val: str,
    dc_val: str,
    decimals: int,
    unit: str,
) -> tuple[AuxPanel, AuxPanel]:
    unit_icon = _unit_file(unit)
    left = AuxPanel(
        _fmt(ac_val, decimals),
        unit_icon,
        aux_char_filename("char_ac.png"),
    )
    right = AuxPanel(
        _fmt(dc_val, decimals),
        unit_icon,
        aux_char_filename("char_dc.png"),
    )
    return left, right


def build_aux_panels(m: Measurement) -> tuple[AuxPanel, AuxPanel]:
    """Vrátí (levý, pravý) horní aux displej pro dané měření."""
    kind = m.kind
    empty = AuxPanel()

    if kind == "VAC":
        left = AuxPanel(_fmt(m.third_val, 2), _unit_file(m.third_unit or "Hz"))
        right = AuxPanel(_fmt(m.sec_val, 1), _unit_file(m.sec_unit or "%"))
        return left, right

    if kind == "VDC+AC":
        unit = m.sec_unit or m.third_unit or "V"
        return _combined_aux(m.third_val, m.sec_val, 4, unit)

    if kind == "ADC":
        if not ADC_AUX_DUTY_ENABLED:
            return empty, empty
        right = AuxPanel(_fmt(m.sec_val, 2, int_digits=2), _unit_file(m.sec_unit or "%"))
        return empty, right

    if kind == "AAC":
        left = AuxPanel(_fmt(m.third_val, 2), _unit_file(m.third_unit or "Hz"))
        right = AuxPanel(_fmt(m.sec_val, 1), _unit_file(m.sec_unit or "%"))
        return left, right

    if kind == "ADC+AC":
        unit = m.sec_unit or m.third_unit or "mA"
        return _combined_aux(m.third_val, m.sec_val, 4, unit)

    if kind == "DIODE":
        right = AuxPanel(_fmt(m.sec_val, 1), aux_unit_icon_filename("Ω"))
        return empty, right

    if kind == "FREQ":
        right = AuxPanel(_fmt(m.sec_val, 1), _unit_file(m.sec_unit or "%"))
        return empty, right

    if kind == "TEMP":
        left = AuxPanel(_fmt(m.third_val, 1), _unit_file("°C"))
        right = AuxPanel(_fmt(m.sec_val, 1), _unit_file(m.sec_unit or "°F"))
        return left, right

    return empty, empty
