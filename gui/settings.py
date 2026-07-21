"""Load / save settings.json."""

import json
from copy import deepcopy

from core.config import SETTINGS_PATH
from core.parsing import MODEL, apply_model

DEFAULTS = {
    "target_mac": "",
    "model_name": "",
    "device_counts": 0,
    "window_scale": 1.0,
    "show_graph": False,
    "debug_click_hotspots": False,
    "debug_display_layout": False,
    "mini_app": False,
    "always_on_top": False,
    "raw_console": False,
    "language": "en-US",
}


def apply_saved_model(settings: dict) -> None:
    """Loads the saved multimeter model (RANGE counts) before connecting."""
    name = (settings.get("model_name") or "").strip()
    counts = int(settings.get("device_counts") or 0)
    if name and counts > 0:
        apply_model(name, counts)


def persist_device(settings: dict, *, mac: str, model_name: str, device_counts: int) -> bool:
    """Saves MAC and model to settings; returns True on change."""
    changed = False
    mac = mac.strip()
    if mac and settings.get("target_mac") != mac:
        settings["target_mac"] = mac
        changed = True
    if model_name and settings.get("model_name") != model_name:
        settings["model_name"] = model_name
        settings["device_counts"] = device_counts
        changed = True
    if changed:
        save_settings(settings)
    return changed


def load_settings() -> dict:
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            merged = deepcopy(DEFAULTS)
            merged.update(data)
            return merged
    except (OSError, json.JSONDecodeError):
        pass
    return deepcopy(DEFAULTS)


def save_settings(settings: dict) -> bool:
    """Atomically write settings.json (temp file then replace, avoids corruption)."""
    import tempfile
    tmp = SETTINGS_PATH.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        tmp.replace(SETTINGS_PATH)
        return True
    except OSError:
        return False
