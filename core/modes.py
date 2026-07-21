"""MODE button logic (rotation, group memory)."""

import json
from .config import UI_STATE_PATH
from .controller import COMMANDS, create_command
from .ranges import kind_from_mode_cmd_key

MODE_CYCLE_GROUPS = (
    ("VDC", ("VDC", "VAC", "VDC+VAC")),
    ("ADC", ("ADC", "AAC", "ADC+AAC")),
    ("OHM", ("OHM", "OHM_ONLINE")),
    ("CAP", ("CAP",)),
    ("DIODE", ("DIODE", "CONT")),
    ("Hz", ("HZ", "TEMP")),
)

KIND_TO_CMD = {
    "VDC": "VDC",
    "VAC": "VAC",
    "VDC+AC": "VDC+VAC",
    "ADC": "ADC",
    "AAC": "AAC",
    "ADC+AC": "ADC+AAC",
    "RES": "OHM",
    "RES_ONLINE": "OHM_ONLINE",
    "CAP": "CAP",
    "DIODE": "DIODE",
    "CONT": "CONT",
    "FREQ": "HZ",
    "TEMP": "TEMP",
}

BTN_LABELS = {
    "HZ": "Hz",
    "OHM_ONLINE": "OHM\nONLINE",
    "VDC+VAC": "VDC+VAC",
    "ADC+AAC": "ADC+AAC",
}


def btn_label(cmd_key: str) -> str:
    """Return display label for mode button (with i18n fallback)."""
    from core.i18n import t
    return t(f"mode_btn.{cmd_key}") if cmd_key in BTN_LABELS else cmd_key


class ModeState:
    def __init__(self) -> None:
        self.groups: dict[str, dict] = {}
        self.active_group: str | None = None
        self.last_kind: str | None = None

    def register_group(self, group_id: str, options: tuple[str, ...]) -> None:
        self.groups[group_id] = {"options": options, "index": 0}

    def load(self) -> None:
        try:
            data = json.loads(UI_STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for group_id, idx in data.get("mode_index", {}).items():
            group = self.groups.get(group_id)
            if group and isinstance(idx, int) and 0 <= idx < len(group["options"]):
                group["index"] = idx

    def save(self) -> None:
        data = {"mode_index": {gid: g["index"] for gid, g in self.groups.items()}}
        try:
            UI_STATE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass

    def get_active_kind(self) -> str | None:
        if self.last_kind:
            return self.last_kind
        if not self.active_group:
            return None
        group = self.groups.get(self.active_group)
        if not group:
            return None
        return kind_from_mode_cmd_key(group["options"][group["index"]])

    def current_cmd_key(self, group_id: str) -> str:
        group = self.groups[group_id]
        return group["options"][group["index"]]

    def cycle_group(self, group_id: str) -> bytes:
        group = self.groups[group_id]
        options = group["options"]
        if self.active_group == group_id and len(options) > 1:
            group["index"] = (group["index"] + 1) % len(options)
        self.active_group = group_id
        self.save()
        return create_command(COMMANDS[group["options"][group["index"]]])

    def sync_from_kind(self, kind: str) -> bool:
        """Sync MODE state from measurement kind; True = buttons need redraw."""
        cmd_key = KIND_TO_CMD.get(kind)
        if not cmd_key:
            return False
        for group_id, group in self.groups.items():
            if cmd_key in group["options"]:
                new_index = group["options"].index(cmd_key)
                changed = self.active_group != group_id or group["index"] != new_index
                group["index"] = new_index
                self.active_group = group_id
                if changed:
                    self.save()
                return changed
        return False
