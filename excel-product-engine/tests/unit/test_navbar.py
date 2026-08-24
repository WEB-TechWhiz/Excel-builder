import pytest

from excel_engine.components.navbar import add_navbar
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import WorkbookBuildError
from excel_engine.styles.style_manager import StyleManager


@pytest.fixture
def sheet():
    wb = ExcelWorkbook()
    return wb.add_sheet("Income")


def test_navbar_writes_all_items(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_navbar(sheet, style, ["Dashboard", "Income", "Expenses"], top_left="A1", item_width=2)
    assert sheet.get_value("A1") == "Dashboard"
    assert sheet.get_value("C1") == "Income"
    assert sheet.get_value("E1") == "Expenses"
    assert rng.to_a1() == "A1:F1"


def test_active_item_has_no_hyperlink(sheet):
    style = StyleManager.for_theme("premium")
    add_navbar(sheet, style, ["Dashboard", "Income"], top_left="A1", active="Income", item_width=2)
    assert sheet.raw["A1"].hyperlink is not None
    assert sheet.raw["C1"].hyperlink is None


def test_active_item_uses_bold_active_font(sheet):
    style = StyleManager.for_theme("premium")
    add_navbar(sheet, style, ["Dashboard", "Income"], top_left="A1", active="Income", item_width=2)
    assert sheet.raw["C1"].font.bold is True
    assert sheet.raw["A1"].font.underline == "single"


def test_navbar_rejects_empty_items(sheet):
    style = StyleManager.for_theme("premium")
    with pytest.raises(WorkbookBuildError):
        add_navbar(sheet, style, [], top_left="A1")
