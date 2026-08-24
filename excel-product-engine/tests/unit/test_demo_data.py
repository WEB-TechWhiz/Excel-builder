import pytest

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.exceptions.errors import WorkbookBuildError
from excel_engine.styles.style_manager import StyleManager


def test_write_demo_rows_writes_correct_cells():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Income")
    style = StyleManager.for_theme("premium")
    write_demo_rows(
        ws, style, headers=["Source", "Amount"],
        rows=[{"Source": "Salary", "Amount": 50000}, {"Source": "Freelance", "Amount": 15000}],
        top_left="A2",
    )
    assert ws.get_value("A2") == "Salary"
    assert ws.get_value("B2") == 50000
    assert ws.get_value("A3") == "Freelance"
    assert ws.get_value("B3") == 15000


def test_write_demo_rows_uses_input_font():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Income")
    style = StyleManager.for_theme("premium")
    write_demo_rows(ws, style, headers=["Source"], rows=[{"Source": "Salary"}], top_left="A2")
    assert ws.raw["A2"].font.color.rgb.endswith("0000FF")


def test_write_demo_rows_rejects_unknown_column():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Income")
    style = StyleManager.for_theme("premium")
    with pytest.raises(WorkbookBuildError):
        write_demo_rows(ws, style, headers=["Source"], rows=[{"Nope": "x"}], top_left="A2")


def test_write_demo_rows_allows_partial_rows():
    """A row doesn't have to fill every header — sparse demo data is fine."""
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Income")
    style = StyleManager.for_theme("premium")
    write_demo_rows(
        ws, style, headers=["Source", "Amount", "Notes"],
        rows=[{"Source": "Salary", "Amount": 50000}], top_left="A2",
    )
    assert ws.get_value("C2") is None
