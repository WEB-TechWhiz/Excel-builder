"""Typography scale — the font half of the design system.

``FontSpec`` holds size/weight only (no color, no family) — color comes
from a ``ColorPalette`` and family from ``Typography.font_family``, so
the same size scale can be reused across every theme.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FontSpec:
    """Size/weight for one typography level."""

    size: float
    bold: bool = False
    italic: bool = False

    def __post_init__(self) -> None:
        if self.size <= 0:
            raise ValueError(f"Font size must be positive, got {self.size}")


@dataclass(frozen=True, slots=True)
class Typography:
    """A full typography scale: title down to caption, one font family."""

    font_family: str = "Arial"
    title: FontSpec = FontSpec(size=20, bold=True)
    heading: FontSpec = FontSpec(size=14, bold=True)
    subheading: FontSpec = FontSpec(size=12, bold=True)
    body: FontSpec = FontSpec(size=10)
    caption: FontSpec = FontSpec(size=9, italic=True)


DEFAULT_TYPOGRAPHY = Typography()
