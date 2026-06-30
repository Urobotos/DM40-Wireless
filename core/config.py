"""Cesty a BLE konstanty projektu."""

import sys
from pathlib import Path


def _install_root() -> Path:
    """Složka s settings.json – vedle .exe nebo kořen projektu."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _resource_root() -> Path:
    """Složka s images/ – v balíku PyInstaller (_MEIPASS) nebo kořen projektu."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", _install_root()))
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = _install_root()
IMAGES_DIR = _resource_root() / "images"
SETTINGS_PATH = PROJECT_ROOT / "settings.json"
UI_STATE_PATH = PROJECT_ROOT / "dm40_ui_state.json"

TARGET_MAC = ""
WRITE_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
CMD_DISCOVERY = b"\xaf\xff\xff\x00\x00\x53"
CMD_POLL = b"\xaf\x05\x03\x09\x00\x40"
POLL_RESPONSE_TIMEOUT = 0.35

# Rozměr UI = gui/layout.py (SCREEN_W × SCREEN_H) × window_scale v settings.json
from gui.layout import SCREEN_H, SCREEN_W

SCREEN_WIDTH = SCREEN_W
SCREEN_HEIGHT = SCREEN_H

# ADC aux2 (duty %) – sniffing.txt dokumentuje -00.00%; vypnout dokud neověříš na HW
ADC_AUX_DUTY_ENABLED = True
