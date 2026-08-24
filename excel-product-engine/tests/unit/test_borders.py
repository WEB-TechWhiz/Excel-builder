from excel_engine.styles.borders import NONE_BORDER, bottom_only, box, build_border


def test_build_border_default_all_sides():
    b = build_border()
    assert b.left.style == "thin"
    assert b.right.style == "thin"
    assert b.top.style == "thin"
    assert b.bottom.style == "thin"


def test_bottom_only_leaves_other_sides_unset():
    b = bottom_only()
    assert b.bottom.style == "thin"
    assert b.left is None
    assert b.top is None


def test_box_uses_given_color():
    b = box(color="FF0000")
    assert b.top.color.rgb.endswith("FF0000")
    assert b.left.color.rgb.endswith("FF0000")


def test_none_border_has_no_sides():
    assert NONE_BORDER.left is None
    assert NONE_BORDER.bottom is None
