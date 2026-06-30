"""Tmavý title bar ve Windows (DWM) – aktivní i neaktivní okno."""

from __future__ import annotations

import sys
import tkinter as tk

DEFAULT_CAPTION = "#292C31"
DEFAULT_TEXT = "#F7F7F7"

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_BORDER_COLOR = 34
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36


def _hex_to_colorref(hex_color: str) -> int:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b << 16) | (g << 8) | r


def _hwnd(root: tk.Tk) -> int | None:
    try:
        import ctypes

        wid = root.winfo_id()
        if not wid:
            return None
        hwnd = ctypes.windll.user32.GetParent(wid)
        return hwnd or wid
    except Exception:
        return None


def _set_dwm_attr(hwnd: int, attr: int, value: int) -> None:
    try:
        import ctypes

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, attr, ctypes.byref(ctypes.c_int(value)), ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


def apply_windows_titlebar(
    root: tk.Tk,
    *,
    caption: str = DEFAULT_CAPTION,
    text: str = DEFAULT_TEXT,
) -> None:
    """Tmavý title bar. Volat jen když je okno viditelné (ne iconified)."""
    if sys.platform != "win32":
        return
    try:
        if root.state() == "iconic":
            return
    except tk.TclError:
        return

    hwnd = _hwnd(root)
    if not hwnd:
        return

    # 2 = vždy tmavý (Win11); 1 = fallback na starších buildách
    _set_dwm_attr(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 2)
    _set_dwm_attr(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 1)
    cap = _hex_to_colorref(caption)
    txt = _hex_to_colorref(text)
    _set_dwm_attr(hwnd, DWMWA_BORDER_COLOR, cap)
    _set_dwm_attr(hwnd, DWMWA_CAPTION_COLOR, cap)
    _set_dwm_attr(hwnd, DWMWA_TEXT_COLOR, txt)


def schedule_windows_titlebar(root: tk.Tk, **kwargs) -> None:
    """Tmavý title bar po startu a znovu při změně fokusu (neaktivní okno)."""
    pending: dict[str, str | None] = {"id": None}

    def _apply() -> None:
        pending["id"] = None
        if root.winfo_exists():
            apply_windows_titlebar(root, **kwargs)

    def _schedule(_event=None) -> None:
        if pending["id"] is not None:
            root.after_cancel(pending["id"])
        pending["id"] = root.after(50, _apply)

    root.after_idle(_apply)
    for seq in ("<FocusIn>", "<FocusOut>", "<Map>"):
        root.bind(seq, _schedule, add="+")


def _bottom_gap_px(root: tk.Tk, content: tk.Widget) -> int:
    """Prázdný pruh pod obsahem (screen coords) – typicky chybně navýšené okno."""
    root.update_idletasks()
    window_bottom = root.winfo_rooty() + root.winfo_height()
    content_bottom = content.winfo_rooty() + content.winfo_height()
    return max(0, window_bottom - content_bottom)


def fit_toplevel_to_client(root: tk.Tk, content: tk.Widget, client_w: int, client_h: int) -> None:
    """Nastaví okno na přesnou velikost canvasu (Tk na Windows = bez extra chrome padding)."""
    root.minsize(client_w, client_h)
    root.geometry(f"{client_w}x{client_h}")
    root.update_idletasks()
    root.update()
    gap = _bottom_gap_px(root, content)
    if gap > 1:
        root.geometry(f"{root.winfo_width()}x{root.winfo_height() - gap}")
        root.update_idletasks()
