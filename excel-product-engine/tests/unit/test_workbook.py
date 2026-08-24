import pytest

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import ExportError, SheetNotFoundError


def test_add_and_get_sheet():
    wb = ExcelWorkbook()
    sheet = wb.add_sheet("Dashboard")
    assert sheet.name == "Dashboard"
    assert wb.get_sheet("Dashboard") is sheet
    assert wb.sheet_names == ["Dashboard"]


def test_default_sheet_is_replaced_not_duplicated():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    wb.add_sheet("Income")
    assert wb.raw.sheetnames == ["Dashboard", "Income"]


def test_missing_sheet_raises():
    wb = ExcelWorkbook()
    with pytest.raises(SheetNotFoundError):
        wb.get_sheet("Nope")


def test_remove_sheet():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    wb.add_sheet("Income")
    wb.remove_sheet("Income")
    assert wb.sheet_names == ["Dashboard"]
    assert not wb.has_sheet("Income")


def test_save_requires_at_least_one_sheet(tmp_path):
    wb = ExcelWorkbook()
    with pytest.raises(ExportError):
        wb.save(tmp_path / "empty.xlsx")


def test_save_and_reload_roundtrip(tmp_path):
    wb = ExcelWorkbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_value("A1", "Financial OS")
    dashboard.set_formula("B1", "=1+1")
    out_path = wb.save(tmp_path / "financial_os.xlsx")

    reloaded = ExcelWorkbook.load(out_path)
    assert reloaded.sheet_names == ["Dashboard"]
    assert reloaded.get_sheet("Dashboard").get_value("A1") == "Financial OS"
    assert reloaded.get_sheet("Dashboard").get_value("B1") == "=1+1"


def test_sheet_names_reflects_reorder():
    """Regression test: sheet_names must track actual tab order, not the
    order sheets were originally added in.
    """
    wb = ExcelWorkbook()
    wb.add_sheet("Orders")
    wb.add_sheet("Dashboard")
    assert wb.sheet_names == ["Orders", "Dashboard"]

    wb.reorder_sheet("Dashboard", index=0)
    assert wb.sheet_names == ["Dashboard", "Orders"]
    assert wb.raw.sheetnames == ["Dashboard", "Orders"]
