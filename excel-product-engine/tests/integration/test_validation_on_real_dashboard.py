"""Proves the validation engine works against a real, full dashboard —
built the same way tests/integration/test_full_dashboard_phase6.py
does — and that it actually catches deliberately-introduced problems,
not just that it runs without crashing.
"""

from datetime import date

from excel_engine.charts import add_bar_chart
from excel_engine.components import add_kpi_card, add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.data.tables import ColumnSchema, add_typed_table
from excel_engine.formulas import Formula
from excel_engine.navigation import apply_menu_to_all_sheets
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager
from excel_engine.validation import validate_workbook


def _build_dashboard() -> ExcelWorkbook:
    style = StyleManager.for_theme("premium")
    workbook = ExcelWorkbook()

    orders = workbook.add_sheet("Orders")
    columns = [
        ColumnSchema(header="Date", type="date"),
        ColumnSchema(header="Colorway", type="list", options=("Amber", "Teal")),
        ColumnSchema(header="Amount", type="currency"),
    ]
    table = add_typed_table(orders, style, columns, n_rows=20, table_name="Orders")
    write_demo_rows(
        orders, style, headers=["Date", "Colorway", "Amount"],
        rows=[{"Date": date(2026, 7, 1), "Colorway": "Amber", "Amount": 2499}],
        top_left="A2",
    )
    apply_standard_protection(
        orders, editable_ranges=[f"A{table.first_data_row}:C{table.last_data_row}"]
    )

    dashboard = workbook.add_sheet("Dashboard")
    workbook.reorder_sheet("Dashboard", index=0)
    add_title_banner(dashboard, style, "Sales Dashboard", top_left="A1", width=9)
    add_kpi_card(dashboard, style, "Total Revenue", Formula.sum("Orders", "Amount"),
                 top_left="A5", number_format='"₹"#,##0')
    add_bar_chart(
        dashboard, style, "Revenue by Colorway", "Orders", "Colorway", "Amount",
        ["Amber", "Teal"], anchor_cell="B9", data_top_left="T5",
    )

    apply_menu_to_all_sheets(workbook, style, ["Dashboard", "Orders"], top_left="A25")
    return workbook


def test_a_well_built_dashboard_passes_full_validation():
    workbook = _build_dashboard()
    report = validate_workbook(
        workbook,
        product_name="Sales Dashboard",
        required_sheets=["Dashboard", "Orders"],
        required_tables={"Orders": ["Orders"]},
        expected_formula_cells=[("Dashboard", "A6")],  # KPI card's value cell
        expected_locked_formula_cells=[("Dashboard", "A6")],
        expected_unlocked_input_ranges=[("Orders", "A2:C21")],
    )
    assert report.passed is True, report.format()
    assert "STATUS: PASS" in report.format()


def test_a_workbook_with_a_broken_reference_fails_formula_validation():
    workbook = _build_dashboard()
    dashboard = workbook.get_sheet("Dashboard")
    dashboard.set_formula("Z1", "=SUM(NotARealTable[Amount])")

    report = validate_workbook(workbook, product_name="Sales Dashboard")
    formula_result = next(r for r in report.results if r.category == "Formulas")
    assert formula_result.passed is False
    assert any("NotARealTable" in i.message for i in formula_result.issues)
    # unrelated categories are unaffected by this one broken formula
    structure_result = next(r for r in report.results if r.category == "Structure")
    assert structure_result.passed is True


def test_a_workbook_missing_a_required_sheet_fails_structure_only():
    workbook = _build_dashboard()
    report = validate_workbook(
        workbook, product_name="Sales Dashboard",
        required_sheets=["Dashboard", "Orders", "Goals"],
    )
    assert report.passed is False
    structure_result = next(r for r in report.results if r.category == "Structure")
    assert structure_result.passed is False
    assert "Goals" in structure_result.issues[0].message


def test_a_workbook_with_a_dangling_navbar_link_fails_integrity():
    workbook = _build_dashboard()
    dashboard = workbook.get_sheet("Dashboard")
    dashboard.raw["Z2"].hyperlink = "#Reports!A1"  # "Reports" sheet doesn't exist

    report = validate_workbook(workbook, product_name="Sales Dashboard")
    integrity_result = next(r for r in report.results if r.category == "Integrity")
    assert integrity_result.passed is False
    assert any("Reports" in i.message for i in integrity_result.issues)
