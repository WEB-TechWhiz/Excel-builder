import pytest

from excel_engine.components.buttons import add_button
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.styles.style_manager import StyleManager


@pytest.fixture
def sheet():
    wb = ExcelWorkbook()
    return wb.add_sheet("Dashboard")


def test_button_writes_label(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_button(sheet, style, "Add New Entry", top_left="B2")
    assert sheet.get_value("B2") == "Add New Entry"
    assert rng.to_a1() == "B2:D2"


def test_button_without_target_has_no_hyperlink(sheet):
    style = StyleManager.for_theme("premium")
    add_button(sheet, style, "Add New Entry", top_left="B2")
    assert sheet.raw["B2"].hyperlink is None


def test_button_with_target_sets_internal_hyperlink(sheet):
    style = StyleManager.for_theme("premium")
    add_button(sheet, style, "Back to Dashboard", top_left="B2", target_sheet="Dashboard")
    assert sheet.raw["B2"].hyperlink.target == "#Dashboard!A1"


def test_button_target_sheet_name_with_space_is_quoted(sheet):
    style = StyleManager.for_theme("premium")
    add_button(sheet, style, "Go", top_left="B2", target_sheet="Order Data")
    assert sheet.raw["B2"].hyperlink.target == "#'Order Data'!A1"
