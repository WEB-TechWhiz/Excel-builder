import pytest

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import WorkbookBuildError
from excel_engine.navigation.hyperlinks import validate_all_hyperlinks
from excel_engine.navigation.menu import apply_menu_to_all_sheets
from excel_engine.styles.style_manager import StyleManager


def test_menu_adds_navbar_to_every_sheet():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    wb.add_sheet("Orders")
    wb.add_sheet("Goals")
    style = StyleManager.for_theme("premium")

    apply_menu_to_all_sheets(wb, style, ["Dashboard", "Orders", "Goals"], item_width=2)

    assert wb.get_sheet("Dashboard").get_value("A1") == "Dashboard"
    assert wb.get_sheet("Orders").get_value("A1") == "Dashboard"
    assert wb.get_sheet("Goals").get_value("A1") == "Dashboard"


def test_each_sheet_shows_itself_as_active():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    wb.add_sheet("Orders")
    style = StyleManager.for_theme("premium")

    apply_menu_to_all_sheets(wb, style, ["Dashboard", "Orders"], item_width=2)

    # On the Orders sheet, "Orders" (at C1) is active -> bold, no link.
    orders_ws = wb.get_sheet("Orders")
    assert orders_ws.raw["C1"].font.bold is True
    assert orders_ws.raw["C1"].hyperlink is None
    assert orders_ws.raw["A1"].hyperlink is not None  # "Dashboard" is a real link here


def test_menu_referencing_missing_sheet_raises_before_writing_anything():
    wb = ExcelWorkbook()
    dashboard = wb.add_sheet("Dashboard")
    style = StyleManager.for_theme("premium")

    with pytest.raises(WorkbookBuildError):
        apply_menu_to_all_sheets(wb, style, ["Dashboard", "Goals"])

    assert dashboard.get_value("A1") is None  # nothing was written


def test_menu_links_all_pass_hyperlink_validation():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    wb.add_sheet("Orders")
    wb.add_sheet("Goals")
    style = StyleManager.for_theme("premium")
    apply_menu_to_all_sheets(wb, style, ["Dashboard", "Orders", "Goals"], item_width=2)
    assert validate_all_hyperlinks(wb) == []
