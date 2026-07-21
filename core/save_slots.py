"""Five save slots below main digits – save a reading by clicking the measurement."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.display_format import combined_main_value_str, split_main_value
from core.parsing import Measurement
from core.save_units import save_unit_filename

SAVE_SLOT_COUNT = 5


@dataclass
class SavedReading:
    text: str = ""
    unit_file: str | None = None


@dataclass
class SaveSlotManager:
    slots: list[SavedReading] = field(default_factory=lambda: [SavedReading() for _ in range(SAVE_SLOT_COUNT)])
    next_index: int = 0
    last_index: int | None = None

    def save(self, text: str, unit_file: str | None) -> int:
        idx = self.next_index
        self.slots[idx] = SavedReading(text, unit_file)
        self.last_index = idx
        self.next_index = (idx + 1) % SAVE_SLOT_COUNT
        return idx

    def clear_all(self) -> None:
        self.slots = [SavedReading() for _ in range(SAVE_SLOT_COUNT)]
        self.next_index = 0
        self.last_index = None


def format_save_reading(m: Measurement) -> tuple[str, str | None]:
    """Return (text, unit_png) for saving to a save slot."""
    main_text = combined_main_value_str(
        m.kind, m.value_str, m.decimals,
        m.sec_val, m.third_val,
        overload=m.overload,
    )
    unit_file = save_unit_filename(m.kind, m.display_unit)

    if m.overload or main_text == "OL":
        return "OL", unit_file

    sign, body, mode = split_main_value(main_text, m.decimals)
    if mode == "ol":
        return "OL", unit_file
    if mode == "text":
        return body, unit_file
    return sign + body, unit_file
