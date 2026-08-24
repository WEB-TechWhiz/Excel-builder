"""Proves Phase 6 (charts, navigation, protection) works together on a
real, complete dashboard — not just in isolation — and that the
chart-backing formulas actually calculate correctly (LibreOffice
recalc), not just that they're well-formed text.
"""

import json
import subprocess
import sys
from datetime import date

from pathlib import Path

from excel_engine.charts import add_bar_chart, add_doughnut_chart, add_line_chart, add_pie_chart
from excel_engine.components import add_kpi_card, add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.data.tables import ColumnSchema, add_typed_table
from excel_engine.formulas import Formula
from excel_engine.navigation import apply_menu_to_all_sheets, validate_all_hyperlinks
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager

RECALC_SCRIPT = str(Path(__file__).resolve().parents[2] / "scripts" / "recalc.py")


def test_full_dashboard_with_charts_nav_and_protection(tmp_path):
    style = StyleManager.for_theme("premium")
    workbook = ExcelWorkbook()

    orders = workbook.add_sheet("Orders")
    columns = [
        ColumnSchema(header="Date", type="date"),
        ColumnSchema(header="Colorway", type="list", options=("Amber", "Teal", "Plum")),
        ColumnSchema(header="Amount", type="currency"),
    ]
    table = add_typed_table(orders, style, columns, n_rows=30, table_name="Orders")
    write_demo_rows(
        orders, style, headers=["Date", "Colorway", "Amount"],
        rows=[
            {"Date": date(2026, 7, 1), "Colorway": "Amber", "Amount": 2499},
            {"Date": date(2026, 7, 4), "Colorway": "Teal", "Amount": 1899},
            {"Date": date(2026, 8, 2), "Colorway": "Amber", "Amount": 3200},
            {"Date": date(2026, 8, 10), "Colorway": "Plum", "Amount": 1500},
        ],
        top_left="A2",
    )
    apply_standard_protection(
        orders, editable_ranges=[f"A{table.first_data_row}:C{table.last_data_row}"]
    )

    goals = workbook.add_sheet("Goals")
    goals.set_value("A1", "placeholder")

    dashboard = workbook.add_sheet("Dashboard")
    workbook.reorder_sheet("Dashboard", index=0)
    add_title_banner(dashboard, style, "Sales Dashboard", subtitle="Auto-calculated",
                      top_left="A1", width=9)
    add_kpi_card(dashboard, style, "Total Revenue", Formula.sum("Orders", "Amount"),
                 top_left="A5", number_format='"₹"#,##0')

    add_bar_chart(
        dashboard, style, "Revenue by Colorway", "Orders", "Colorway", "Amount",
        ["Amber", "Teal", "Plum"], anchor_cell="B9", data_top_left="T5",
    )
    add_pie_chart(
        dashboard, style, "Share by Colorway", "Orders", "Colorway", "Amount",
        ["Amber", "Teal", "Plum"], anchor_cell="K9", data_top_left="T12",
    )
    add_doughnut_chart(
        dashboard, style, "Share (doughnut)", "Orders", "Colorway", "Amount",
        ["Amber", "Teal", "Plum"], anchor_cell="B27", data_top_left="T19",
    )
    add_line_chart(
        dashboard, style, "Revenue Trend", "Orders", "Date", "Amount",
        anchor_cell="K27", data_top_left="T25", periods=6, as_of=date(2026, 8, 15),
    )

    apply_menu_to_all_sheets(workbook, style, ["Dashboard", "Orders", "Goals"],
                              top_left="A45", item_width=3)

    assert validate_all_hyperlinks(workbook) == []

    out_path = workbook.save(tmp_path / "sales_dashboard.xlsx")

    result = subprocess.run(
        [sys.executable, RECALC_SCRIPT, str(out_path), "30"],
        capture_output=True, text=True, timeout=90,
    )
    report = json.loads(result.stdout)
    assert report["status"] == "success", report
    assert report["total_errors"] == 0

    import openpyxl

    raw = openpyxl.load_workbook(str(out_path))
    assert len(raw["Dashboard"]._charts) == 4
    assert raw["Orders"].protection.sheet is True
