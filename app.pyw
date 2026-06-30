"""DM40 Wireless – entry point (no console window on Windows)."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from gui.app_window import run_app

if __name__ == "__main__":
    run_app()
