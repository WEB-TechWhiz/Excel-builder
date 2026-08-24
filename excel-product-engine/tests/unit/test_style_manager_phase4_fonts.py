from excel_engine.styles.style_manager import StyleManager


def test_subtitle_font_uses_on_primary_color():
    sm = StyleManager.for_theme("premium")
    assert sm.subtitle_font.color.rgb.endswith(sm.palette.on_primary)


def test_nav_link_font_is_underlined_and_primary_colored():
    sm = StyleManager.for_theme("premium")
    assert sm.nav_link_font.underline == "single"
    assert sm.nav_link_font.color.rgb.endswith(sm.palette.primary)


def test_nav_active_font_is_bold_not_underlined():
    sm = StyleManager.for_theme("premium")
    assert sm.nav_active_font.bold is True
    assert sm.nav_active_font.underline is None
