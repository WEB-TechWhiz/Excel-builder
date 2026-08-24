import pytest

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import WorkbookBuildError
from excel_engine.navigation.hyperlinks import internal_link, validate_all_hyperlinks


def test_internal_link_to_existing_sheet():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    wb.add_sheet("Orders")
    assert internal_link(wb, "Orders") == "#Orders!A1"


def test_internal_link_quotes_spaced_sheet_name():
    wb = ExcelWorkbook()
    wb.add_sheet("Order Data")
    assert internal_link(wb, "Order Data") == "#'Order Data'!A1"


def test_internal_link_to_missing_sheet_raises():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    with pytest.raises(WorkbookBuildError):
        internal_link(wb, "DoesNotExist")


def test_validate_all_hyperlinks_finds_nothing_wrong_by_default():
    wb = ExcelWorkbook()
    dashboard = wb.add_sheet("Dashboard")
    orders = wb.add_sheet("Orders")
    dashboard.raw["A1"].hyperlink = internal_link(wb, "Orders")
    orders.raw["A1"].hyperlink = internal_link(wb, "Dashboard")
    assert validate_all_hyperlinks(wb) == []


def test_validate_all_hyperlinks_catches_a_dangling_link():
    """A link built by hand (bypassing internal_link) can still point
    nowhere — validate_all_hyperlinks catches it after the fact.
    """
    wb = ExcelWorkbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.raw["B2"].hyperlink = "#Goals!A1"  # "Goals" sheet doesn't exist

    problems = validate_all_hyperlinks(wb)
    assert len(problems) == 1
    assert "Goals" in problems[0]
    assert "Dashboard!B2" in problems[0]


def test_validate_all_hyperlinks_ignores_external_links():
    wb = ExcelWorkbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.raw["A1"].hyperlink = "https://example.com"
    assert validate_all_hyperlinks(wb) == []
