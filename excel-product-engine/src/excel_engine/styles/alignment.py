"""Alignment presets — the alignment half of the design system."""

from __future__ import annotations

from openpyxl.styles import Alignment

CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center")
RIGHT = Alignment(horizontal="right", vertical="center")
WRAP = Alignment(horizontal="left", vertical="top", wrap_text=True)


def indented(horizontal: str = "left", indent: int = 1) -> Alignment:
    return Alignment(horizontal=horizontal, vertical="center", indent=indent)
