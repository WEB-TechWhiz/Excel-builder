"""Net Worth sheet: dated Asset/Liability line items. Net Worth itself
(Assets - Liabilities) is computed on the Dashboard, not stored here —
this sheet is the log of what makes it up, snapshotted whenever the
user updates it (typically monthly), which is also what feeds the
Dashboard's Net Worth Trend chart.
"""

from __future__ import annotations

from excel_engine.components import add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.data.tables import ColumnSchema, TypedTable, add_typed_table
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.data.demo_data import NET_WORTH_ROWS

COLUMNS = [
    ColumnSchema(header="Date", type="date"),
    ColumnSchema(header="Item", type="text"),
    ColumnSchema(header="Type", type="list", options=("Asset", "Liability")),
    ColumnSchema(header="Category", type="list", options=(
        "Cash", "Bank Account", "Investment", "Property", "Vehicle",
        "Credit Card", "Loan", "Other",
    )),
    ColumnSchema(header="Value", type="currency"),
]

TABLE_NAME = "NetWorth"  # table names can't contain spaces; the sheet/tab name can


def build_net_worth_sheet(workbook: ExcelWorkbook, style: StyleManager) -> TypedTable:
    ws = workbook.add_sheet("Net Worth")
    add_title_banner(
        ws, style, "Net Worth",
        subtitle="Log each asset/liability whenever you update it — re-enter a new "
                 "dated row rather than editing an old one, so the trend stays accurate",
        top_left="A2", width=5,
    )

    table = add_typed_table(ws, style, COLUMNS, n_rows=100, table_name=TABLE_NAME, top_left="A5")
    write_demo_rows(ws, style, headers=[c.header for c in COLUMNS], rows=NET_WORTH_ROWS,
                     top_left=f"A{table.first_data_row}")

    apply_standard_protection(
        ws, editable_ranges=[f"A{table.first_data_row}:E{table.last_data_row}"]
    )
    return table
