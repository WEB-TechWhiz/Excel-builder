import pytest

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import CellAddressError


def test_set_and_get_value():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Dashboard")
    ws.set_value("A1", "Hello")
    assert ws.get_value("A1") == "Hello"


def test_formula_must_start_with_equals():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Dashboard")
    with pytest.raises(CellAddressError):
        ws.set_formula("A1", "SUM(A1:A2)")


def test_merge_and_freeze_panes():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Dashboard")
    ws.merge("A1:C1")
    ws.freeze_panes("A2")
    assert ws.raw.freeze_panes == "A2"


def test_tab_color_and_gridlines():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Dashboard")
    ws.set_tab_color("1F4E78")
    ws.show_gridlines(False)
    assert ws.raw.sheet_view.showGridLines is False
