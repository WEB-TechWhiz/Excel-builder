import pytest

from excel_engine.components.inputs import add_labeled_input
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.styles.style_manager import StyleManager


@pytest.fixture
def sheet():
    wb = ExcelWorkbook()
    return wb.add_sheet("Settings")


def test_labeled_input_writes_label_and_default(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_labeled_input(sheet, style, "Currency", top_left="A1", default_value="INR")
    assert sheet.get_value("A1") == "Currency"
    assert sheet.get_value("C1") == "INR"
    assert rng.to_a1() == "A1:D1"


def test_labeled_input_without_default_leaves_input_blank(sheet):
    style = StyleManager.for_theme("premium")
    add_labeled_input(sheet, style, "Name", top_left="A1")
    assert sheet.get_value("C1") is None


def test_labeled_input_uses_input_font(sheet):
    style = StyleManager.for_theme("premium")
    add_labeled_input(sheet, style, "Currency", top_left="A1", default_value="INR")
    assert sheet.raw["C1"].font.color.rgb.endswith("0000FF")
