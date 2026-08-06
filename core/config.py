"""Project paths and BLE constants."""

import sys
from pathlib import Path


def _install_root() -> Path:
    """Folder with settings.json / i18n / ui state – next to .exe, or project root in dev.

    Dev (``DM40 Wireless.bat`` / ``python app.py``): project root via ``__file__``.
    Nuitka / PyInstaller: directory of the running executable so files stay beside
    the exe (e.g. ``dist\\DM40 Wireless\\``), not a parent folder like ``dist\\``.
    """
    compiled = globals().get("__compiled__")
    if compiled is not None:
        # Prefer argv0 / sys.executable over __compiled__.containing_dir — with
        # Nuitka --standalone, containing_dir can resolve to the parent of the
        # distribution folder (dist/) instead of the folder that holds the exe.
        for candidate in (sys.argv[0], sys.executable):
            try:
                exe = Path(candidate).resolve()
            except OSError:
                continue
            if exe.is_file() and exe.suffix.lower() == ".exe":
                return exe.parent
        if hasattr(compiled, "containing_dir"):
            return Path(compiled.containing_dir)
        return Path(sys.argv[0]).resolve().parent
    if getattr(sys, "frozen", False):
        # PyInstaller / cx_Freeze
        return Path(sys.executable).resolve().parent
    # Development: core/config.py → project root
    return Path(__file__).resolve().parent.parent


def _resource_root() -> Path:
    """Folder with images/ – PyInstaller (_MEIPASS), Nuitka (__file__), or dev root."""
    if globals().get("__compiled__") is not None:
        # Nuitka (--standalone / --onefile): __file__ is inside the bundle
        # (standalone folder or onefile extract dir). config.py lives at
        # <root>/core/config.py, so .parent.parent is the bundle root.
        # Images are packed via --include-data-dir, alongside __file__.
        return Path(__file__).resolve().parent.parent
    if getattr(sys, "frozen", False):
        # PyInstaller stores bundled data under sys._MEIPASS
        meipass: str | None = getattr(sys, "_MEIPASS", None)
        if meipass is not None:
            return Path(meipass)
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = _install_root()
IMAGES_DIR = _resource_root() / "images"
I18N_DIR = PROJECT_ROOT / "i18n"
EMBEDDED_I18N_DIR = _resource_root() / "i18n"  # Fallback inside exe (Nuitka --include-data-files)
SETTINGS_PATH = PROJECT_ROOT / "settings.json"
UI_STATE_PATH = PROJECT_ROOT / "dm40_ui_state.json"

TARGET_MAC = ""
WRITE_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
CMD_DISCOVERY = b"\xaf\xff\xff\x00\x00\x53"
CMD_POLL = b"\xaf\x05\x03\x09\x00\x40"
POLL_RESPONSE_TIMEOUT = 0.35

# UI size = gui/layout.py (SCREEN_W × SCREEN_H) × window_scale in settings.json
from gui.layout import SCREEN_H, SCREEN_W

SCREEN_WIDTH = SCREEN_W
SCREEN_HEIGHT = SCREEN_H

# ADC aux2 (duty %) – sniffing.txt documents -00.00%; disable until verified on hardware
ADC_AUX_DUTY_ENABLED = True
