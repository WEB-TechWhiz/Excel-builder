import pytest

from excel_engine.config.themes import AVAILABLE_THEMES
from excel_engine.exceptions.errors import ProductConfigurationError
from excel_engine.styles.colors import THEME_PALETTES, ColorPalette, get_palette


def test_every_registered_theme_has_a_palette():
    for theme in AVAILABLE_THEMES:
        assert theme in THEME_PALETTES


def test_get_palette_returns_matching_palette():
    palette = get_palette("premium")
    assert palette.primary == "1F4E78"


def test_get_palette_unknown_theme_raises():
    with pytest.raises(ProductConfigurationError):
        get_palette("not-a-theme")


def test_hex_values_are_uppercased():
    palette = ColorPalette(
        primary="1f4e78", secondary="c9a227", background="ffffff", surface="eaf0f8",
        text="1a1a1a", muted="6b7280", success="2e7d32", warning="b7791f", danger="b3261e",
    )
    assert palette.primary == "1F4E78"
    assert palette.secondary == "C9A227"


def test_invalid_hex_raises():
    with pytest.raises(ProductConfigurationError):
        ColorPalette(
            primary="not-a-color", secondary="C9A227", background="FFFFFF", surface="EAF0F8",
            text="1A1A1A", muted="6B7280", success="2E7D32", warning="B7791F", danger="B3261E",
        )


def test_on_primary_defaults_to_white():
    palette = get_palette("classic")
    assert palette.on_primary == "FFFFFF"
