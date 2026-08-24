from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.tables import ColumnSchema, add_typed_table
from excel_engine.formulas import Formula
from excel_engine.styles.style_manager import StyleManager
from excel_engine.validation.workbook_validator import validate_workbook


def test_validate_workbook_runs_all_four_categories():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    report = validate_workbook(wb, product_name="Test Product")
    categories = [r.category for r in report.results]
    assert categories == ["Structure", "Formulas", "Integrity", "Protection"]


def test_validate_workbook_passes_for_a_well_built_workbook():
    wb = ExcelWorkbook()
    style = StyleManager.for_theme("premium")
    orders = wb.add_sheet("Orders")
    add_typed_table(orders, style, [ColumnSchema(header="Amount", type="currency")],
                     n_rows=10, table_name="Orders")
    dashboard = wb.add_sheet("Dashboard")
    dashboard.set_formula("A1", Formula.sum("Orders", "Amount"))

    report = validate_workbook(
        wb, product_name="Sales Tracker",
        required_sheets=["Dashboard", "Orders"],
        required_tables={"Orders": ["Orders"]},
        expected_formula_cells=[("Dashboard", "A1")],
    )
    assert report.passed is True, report.format()


def test_validate_workbook_fails_and_reports_which_category():
    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    report = validate_workbook(wb, product_name="Sales Tracker",
                                required_sheets=["Dashboard", "Orders"])
    assert report.passed is False
    structure_result = next(r for r in report.results if r.category == "Structure")
    assert structure_result.passed is False
    formula_result = next(r for r in report.results if r.category == "Formulas")
    assert formula_result.passed is True  # unrelated category still passes independently
