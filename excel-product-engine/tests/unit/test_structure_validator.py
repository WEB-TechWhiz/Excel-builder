from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.named_ranges import add_named_range
from excel_engine.data.tables import ColumnSchema, add_typed_table
from excel_engine.styles.style_manager import StyleManager
from excel_engine.validation.structure_validator import validate_structure


def test_all_required_sheets_present():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    wb.add_sheet("Orders")
    result = validate_structure(wb, required_sheets=["Dashboard", "Orders"])
    assert result.passed is True


def test_missing_required_sheet_fails():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    result = validate_structure(wb, required_sheets=["Dashboard", "Orders"])
    assert result.passed is False
    assert "Orders" in result.issues[0].message


def test_required_table_present():
    wb = ExcelWorkbook()
    style = StyleManager.for_theme("premium")
    ws = wb.add_sheet("Orders")
    add_typed_table(ws, style, [ColumnSchema(header="Amount", type="currency")],
                     n_rows=5, table_name="Orders")
    result = validate_structure(wb, required_tables={"Orders": ["Orders"]})
    assert result.passed is True


def test_missing_required_table_fails():
    wb = ExcelWorkbook()
    wb.add_sheet("Orders")
    result = validate_structure(wb, required_tables={"Orders": ["Orders"]})
    assert result.passed is False
    assert "Orders" in result.issues[0].message


def test_required_named_range_present():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Orders")
    ws.set_value("A1", 100)
    add_named_range(wb, "TotalAmount", sheet="Orders", cell_range="A1")
    result = validate_structure(wb, required_named_ranges=["TotalAmount"])
    assert result.passed is True


def test_missing_named_range_fails():
    wb = ExcelWorkbook()
    wb.add_sheet("Orders")
    result = validate_structure(wb, required_named_ranges=["TotalAmount"])
    assert result.passed is False


def test_no_requirements_always_passes():
    wb = ExcelWorkbook()
    wb.add_sheet("Anything")
    result = validate_structure(wb)
    assert result.passed is True
