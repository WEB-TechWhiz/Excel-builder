from excel_engine.styles.alignment import CENTER, LEFT, RIGHT, WRAP, indented


def test_presets():
    assert CENTER.horizontal == "center"
    assert LEFT.horizontal == "left"
    assert RIGHT.horizontal == "right"
    assert WRAP.wrap_text is True
    assert WRAP.vertical == "top"


def test_indented_default():
    a = indented()
    assert a.indent == 1
    assert a.horizontal == "left"


def test_indented_custom():
    a = indented(horizontal="right", indent=3)
    assert a.horizontal == "right"
    assert a.indent == 3
