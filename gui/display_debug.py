"""Poloprůhledné debug obdélníky pro ladění layoutu displeje."""

from __future__ import annotations

import tkinter as tk

DEBUG_DISPLAY_TAG = "debug_display"


def clear_display_debug(canvas: tk.Canvas) -> None:
    canvas.delete(DEBUG_DISPLAY_TAG)


def draw_debug_rect(
    canvas: tk.Canvas,
    x: int,
    y: int,
    w: int,
    h: int,
    color: str,
    *,
    scale: float = 1.0,
) -> int:
    sx, sy, sw, sh = int(x * scale), int(y * scale), int(w * scale), int(h * scale)
    return canvas.create_rectangle(
        sx, sy, sx + sw, sy + sh,
        fill=color,
        outline=color,
        width=1,
        stipple="gray50",
        tags=(DEBUG_DISPLAY_TAG,),
    )
