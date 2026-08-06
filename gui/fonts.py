"""GUI font family from settings.json (default Arial for consistent Windows rendering)."""

DEFAULT_GUI_FONT = "Arial"


def gui_font_family(settings: dict | None = None) -> str:
    """Return configured GUI font family."""
    if settings:
        name = (settings.get("gui_font") or "").strip()
        if name:
            return name
    return DEFAULT_GUI_FONT


def gui_font(settings: dict | None, size: int, weight: str = "normal") -> tuple[str, int, str]:
    """Tk font tuple (family, size, weight)."""
    return (gui_font_family(settings), size, weight)
