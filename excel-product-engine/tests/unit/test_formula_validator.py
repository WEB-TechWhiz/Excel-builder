from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.tables import ColumnSchema, add_typed_table
from excel_engine.formulas import Formula
from excel_engine.styles.style_manager import StyleManager
from excel_engine.validation.formula_validator import validate_formulas


def _orders_workbook():
    wb = ExcelWorkbook()
    style = StyleManager.for_theme("premium")
    ws = wb.add_sheet("Orders")
    add_typed_table(
        ws, style,
        [ColumnSchema(header="Colorway", type="list", options=("Amber",)),
         ColumnSchema(header="Amount", type="currency")],
        n_rows=10, table_name="Orders",
    )
    return wb


def test_valid_structured_reference_passes():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", Formula.sum("Orders", "Amount"))
    result = validate_formulas(wb)
    assert result.passed is True


def test_reference_to_missing_table_fails():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", "=SUM(Invoices[Amount])")
    result = validate_formulas(wb)
    assert result.passed is False
    assert "Invoices" in result.issues[0].message


def test_reference_to_missing_column_fails():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", "=SUM(Orders[Discount])")
    result = validate_formulas(wb)
    assert result.passed is False
    assert "Discount" in result.issues[0].message


def test_reference_to_missing_sheet_fails():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", "=SUM(Invoices!A1:A10)")
    result = validate_formulas(wb)
    assert result.passed is False
    assert "Invoices" in result.issues[0].message


def test_valid_plain_sheet_range_passes():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", Formula.sum_range("Orders", "C2:C11"))
    result = validate_formulas(wb)
    assert result.passed is True


def test_broken_ref_error_token_detected():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", "=SUM(#REF!)")
    result = validate_formulas(wb)
    assert result.passed is False
    assert "#REF!" in result.issues[0].message


def test_expected_formula_cell_present():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", Formula.sum("Orders", "Amount"))
    result = validate_formulas(wb, expected_formula_cells=[("Dashboard", "A1")])
    assert result.passed is True


def test_expected_formula_cell_missing_fails():
    wb = _orders_workbook()
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_value("A1", "not a formula")
    result = validate_formulas(wb, expected_formula_cells=[("Dashboard", "A1")])
    assert result.passed is False
