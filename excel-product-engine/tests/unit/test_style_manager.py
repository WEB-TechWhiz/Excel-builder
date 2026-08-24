import pytest

from excel_engine.config.themes import AVAILABLE_THEMES
from excel_engine.exceptions.errors import ProductConfigurationError
from excel_engine.styles.style_manager import Spacing, StyleManager


def test_for_theme_builds_matching_palette():
    sm = StyleManager.for_theme("premium")
    assert sm.palette.primary == "1F4E78"
    assert sm.theme_name == "premium"


def test_for_theme_unknown_raises():
    with pytest.raises(ProductConfigurationError):
        StyleManager.for_theme("not-a-theme")


@pytest.mark.parametrize("theme", AVAILABLE_THEMES)
def test_every_theme_resolves_cleanly(theme):
    sm = StyleManager.for_theme(theme)
    # every style property must resolve without error, for every theme
    assert sm.title_font.name == "Arial"
    assert sm.header_fill.fill_type == "solid"
    assert sm.thin_border.top.style == "thin"
    assert sm.center.horizontal == "center"


def test_title_font_uses_on_primary_color():
    sm = StyleManager.for_theme("premium")
    assert sm.title_font.color.rgb.endswith(sm.palette.on_primary)
    assert sm.title_font.bold is True


def test_input_font_is_always_blue_regardless_of_theme():
    for theme in AVAILABLE_THEMES:
        sm = StyleManager.for_theme(theme)
        assert sm.input_font.color.rgb.endswith("0000FF")


def test_formula_font_is_never_the_input_blue():
    for theme in AVAILABLE_THEMES:
        sm = StyleManager.for_theme(theme)
        assert not sm.formula_font.color.rgb.endswith("0000FF")


def test_header_fill_uses_primary_color():
    sm = StyleManager.for_theme("classic")
    assert sm.header_fill.fgColor.rgb.endswith(sm.palette.primary)


def test_card_fill_uses_surface_color():
    sm = StyleManager.for_theme("minimal")
    assert sm.card_fill.fgColor.rgb.endswith(sm.palette.surface)


def test_spacing_scale_ascends():
    assert Spacing.XS < Spacing.SM < Spacing.MD < Spacing.LG < Spacing.XL < Spacing.XXL
