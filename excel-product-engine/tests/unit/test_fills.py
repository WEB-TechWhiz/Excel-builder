from excel_engine.styles.fills import NO_FILL, solid_fill


def test_solid_fill_sets_fg_color_and_type():
    fill = solid_fill("1F4E78")
    assert fill.fill_type == "solid"
    assert fill.fgColor.rgb.endswith("1F4E78")


def test_no_fill_has_no_fill_type():
    assert NO_FILL.fill_type is None
