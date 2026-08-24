"""Registry of valid theme *names*.

The actual visual definition of each theme (colors, fonts, spacing) lives
in ``excel_engine.styles`` (Phase 3 — not yet implemented). This module
only defines which theme names a ``ProductConfig`` is allowed to
reference, so configuration can be validated before that phase lands.
"""

from __future__ import annotations

AVAILABLE_THEMES: tuple[str, ...] = ("premium", "midnight", "forest", "sunset", "minimal", "classic")


def is_valid_theme(name: str) -> bool:
    return name in AVAILABLE_THEMES
