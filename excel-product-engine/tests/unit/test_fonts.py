import pytest

from excel_engine.styles.fonts import DEFAULT_TYPOGRAPHY, FontSpec, Typography


def test_default_typography_scale_descends():
    t = DEFAULT_TYPOGRAPHY
    assert t.title.size > t.heading.size > t.subheading.size > t.body.size > t.caption.size


def test_font_spec_rejects_non_positive_size():
    with pytest.raises(ValueError):
        FontSpec(size=0)
    with pytest.raises(ValueError):
        FontSpec(size=-2)


def test_typography_custom_family_keeps_default_sizes():
    t = Typography(font_family="Calibri")
    assert t.font_family == "Calibri"
    assert t.body.size == 10


def test_title_is_bold_by_default():
    assert DEFAULT_TYPOGRAPHY.title.bold is True
    assert DEFAULT_TYPOGRAPHY.caption.italic is True
