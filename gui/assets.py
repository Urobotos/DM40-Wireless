"""PNG loading and canvas click areas."""

from pathlib import Path
import tkinter as tk

from core.config import IMAGES_DIR

CLICK_HOTSPOT_TAG = "click_hotspot"


def load_background_photo(path: Path, scale: float = 1.0):
    if not path.is_file():
        return None
    try:
        from PIL import Image, ImageTk
    except ImportError:
        return None
    img = Image.open(path)
    if scale != 1.0:
        w, h = img.size
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def bind_clickable(
    canvas: tk.Canvas,
    x: int,
    y: int,
    w: int,
    h: int,
    command,
    *,
    tag: str | None = None,
    debug: bool = False,
    debug_color: str = "#4080ff",
) -> int:
    """Transparent hit area; must sit above sprites (raise_click_hotspots)."""
    hit_tag = tag or f"hit_{x}_{y}"
    rid = canvas.create_rectangle(
        x, y, x + w, y + h,
        fill=debug_color if debug else "",
        outline=debug_color if debug else "",
        width=1 if debug else 0,
        stipple="gray50" if debug else "",
        tags=(hit_tag, CLICK_HOTSPOT_TAG),
    )

    def _on_click(_event) -> None:
        command()

    canvas.tag_bind(hit_tag, "<Button-1>", _on_click)
    return rid


def raise_click_hotspots(canvas: tk.Canvas) -> None:
    """Raise click layer on top – transparent PNG otherwise swallows clicks."""
    canvas.tag_raise(CLICK_HOTSPOT_TAG)
