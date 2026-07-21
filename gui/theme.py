"""UI colors."""

RGB_COLORS = {
    "background": (8, 16, 24),
    "orange_main": (255, 141, 26),
    "orange_hv_warn": (235, 87, 101),
    "buttons": (41, 44, 49),
    "range_buttons": (24, 32, 33),
    "buttons_active": (0, 130, 206),
    "top_bar_background": (24, 32, 33),
    "save_area": (24, 32, 33),
    "text_primary": (247, 247, 247),
    "text_secondary": (206, 208, 208),
    "graph_grid": (45, 45, 55),
    "graph_text": (100, 100, 100),
}


def rgb_hex(name: str) -> str:
    r, g, b = RGB_COLORS[name]
    return f"#{r:02x}{g:02x}{b:02x}"
