"""DM40 Wireless – dev entry (console shows errors). For daily use: app.pyw or DM40 Wireless.bat."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from gui.app_window import run_app

if __name__ == "__main__":
    run_app()
