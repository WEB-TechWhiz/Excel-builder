"""Border presets — the border half of the design system."""

from __future__ import annotations

from openpyxl.styles import Border, Side

THIN = "thin"
MEDIUM = "medium"
THICK = "thick"


def build_border(
    style: str = THIN,
    color: str = "BFBFBF",
    sides: tuple[str, ...] = ("left", "right", "top", "bottom"),
) -> Border:
    """Build an openpyxl Border with the given style/color on the given sides."""
    side = Side(style=style, color=color)
    kwargs = dict.fromkeys(sides, side)
    return Border(**kwargs)


def box(color: str = "BFBFBF", style: str = THIN) -> Border:
    """A full box border around a single cell."""
    return build_border(style=style, color=color)


def bottom_only(color: str = "BFBFBF", style: str = THIN) -> Border:
    return build_border(style=style, color=color, sides=("bottom",))


NONE_BORDER = Border()
