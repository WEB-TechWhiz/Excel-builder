"""Color palettes — the color half of the design system.

Each theme (see ``excel_engine.config.themes.AVAILABLE_THEMES``) resolves
to one ``ColorPalette``. Everything downstream (fonts, fills, borders,
and components in later phases) pulls colors from here rather than
hard-coding hex values, so changing a theme's look means editing one
dict in this file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, fields

from excel_engine.exceptions.errors import ProductConfigurationError

_HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")


def _validate_hex(name: str, value: str) -> str:
    if not _HEX_RE.match(value):
        raise ProductConfigurationError(
            f"Color {name!r} must be a 6-digit hex string (no '#'), got {value!r}"
        )
    return value.upper()


@dataclass(frozen=True, slots=True)
class ColorPalette:
    """A theme's full color set. All values are 6-digit hex, no '#'."""

    primary: str
    secondary: str
    background: str
    surface: str
    text: str
    muted: str
    success: str
    warning: str
    danger: str
    on_primary: str = "FFFFFF"  # text color to use when painted over `primary`

    def __post_init__(self) -> None:
        for f in fields(self):
            object.__setattr__(self, f.name, _validate_hex(f.name, getattr(self, f.name)))


THEME_PALETTES: dict[str, ColorPalette] = {
    "premium": ColorPalette(
        primary="1F4E78",
        secondary="C9A227",
        background="FFFFFF",
        surface="EAF0F8",
        text="1A1A1A",
        muted="6B7280",
        success="2E7D32",
        warning="B7791F",
        danger="B3261E",
    ),
    "minimal": ColorPalette(
        primary="2B2B2B",
        secondary="8A8A8A",
        background="FFFFFF",
        surface="F5F5F5",
        text="1A1A1A",
        muted="9CA3AF",
        success="3A7D44",
        warning="9C7A22",
        danger="9C2B2B",
    ),
    "classic": ColorPalette(
        primary="205C37",
        secondary="8C6D1F",
        background="FFFFFF",
        surface="E8F1EB",
        text="1A1A1A",
        muted="6B7280",
        success="1E7B34",
        warning="A66A11",
        danger="A32626",
    ),
    # ── Themes matching the excel-builder-app frontend ─────────────────────
    # ARGB values are taken from frontend types.ts THEMES constant (FF prefix stripped).
    "midnight": ColorPalette(
        primary="10192E",   # FF10192E — deep navy
        secondary="3B82F6",  # accent blue
        background="FFFFFF",
        surface="EEF3FC",   # band color FFEEF3FC
        text="FFFFFF",      # on-primary text
        muted="667085",
        success="17B26A",
        warning="F79009",
        danger="F04438",
        on_primary="FFFFFF",
    ),
    "forest": ColorPalette(
        primary="1B3A2B",   # FF1B3A2B — deep forest green
        secondary="6BBF59",  # accent green
        background="FFFFFF",
        surface="F0F6EC",   # band color FFF0F6EC
        text="FFFFFF",
        muted="667085",
        success="6BBF59",
        warning="F79009",
        danger="F04438",
        on_primary="FFFFFF",
    ),
    "sunset": ColorPalette(
        primary="3A1E14",   # FF3A1E14 — deep burnt sienna
        secondary="E8743B",  # accent orange
        background="FFFFFF",
        surface="FCF1EA",   # band color FFFCF1EA
        text="FFFFFF",
        muted="667085",
        success="17B26A",
        warning="E8743B",
        danger="F04438",
        on_primary="FFFFFF",
    ),
}


def get_palette(theme_name: str) -> ColorPalette:
    try:
        return THEME_PALETTES[theme_name]
    except KeyError as exc:
        raise ProductConfigurationError(
            f"No color palette registered for theme {theme_name!r}. "
            f"Available: {list(THEME_PALETTES)}"
        ) from exc
