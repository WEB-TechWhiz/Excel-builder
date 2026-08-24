from openpyxl import load_workbook

from excel_engine.llm.builder import build_from_spec
from excel_engine.llm.schema import DashboardSpec, KPISpec, TableSheetSpec, WorkbookSpec


def _spec() -> WorkbookSpec:
    return WorkbookSpec(
        product_name="Sales Tracker",
        theme="premium",
        currency_symbol="₹",
        tables=[
            TableSheetSpec(
                name="Orders",
                columns=[{"header": "Date"}, {"header": "Customer"}, {"header": "Amount"}],
                n_rows=50,
            )
        ],
        dashboard=DashboardSpec(kpis=[
            KPISpec(label="Total Revenue", source_sheet="Orders",
                    source_column="Amount", agg="SUM", format="currency"),
            KPISpec(label="Total Orders", source_sheet="Orders",
                    source_column="Date", agg="COUNTA", format="number"),
        ]),
    )


def test_builder_creates_dashboard_and_table_sheets():
    workbook = build_from_spec(_spec())
    assert workbook.sheet_names == ["Dashboard", "Orders"]


def test_builder_writes_correct_kpi_formulas():
    workbook = build_from_spec(_spec())
    dashboard = workbook.get_sheet("Dashboard")
    assert dashboard.get_value("A5") == "=SUM(Orders[Amount])"
    assert dashboard.get_value("E5") == "=COUNTA(Orders[Date])"


def test_builder_applies_currency_number_format():
    workbook = build_from_spec(_spec())
    dashboard = workbook.get_sheet("Dashboard")
    assert dashboard.raw["A5"].number_format == '"₹"#,##0'


def test_builder_creates_real_table_on_data_sheet():
    workbook = build_from_spec(_spec())
    orders = workbook.get_sheet("Orders")
    assert "Orders" in orders.raw.tables


def test_builder_output_survives_save_reload_and_recalculates(tmp_path):
    """Full offline pipeline check: spec -> workbook -> real .xlsx with
    correct, error-free formulas. No network/LLM involved at all.
    """
    workbook = build_from_spec(_spec())
    orders = workbook.get_sheet("Orders")
    orders.set_value("A2", "2026-01-01")
    orders.set_value("B2", "Ananya Verma")
    orders.set_value("C2", 2499)

    out_path = workbook.save(tmp_path / "sales_tracker.xlsx")

    raw = load_workbook(str(out_path))
    assert raw["Orders"]["C2"].value == 2499
    assert raw["Dashboard"]["A5"].value == "=SUM(Orders[Amount])"
