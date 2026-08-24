"""Bills sheet: Bill, Category, Due Date, Amount, Status, Recurring, Notes."""

from __future__ import annotations

from excel_engine.components import add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.data.tables import ColumnSchema, TypedTable, add_typed_table
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.data.demo_data import BILLS_ROWS

COLUMNS = [
    ColumnSchema(header="Bill", type="text"),
    ColumnSchema(header="Category", type="list", options=(
        "Utilities", "Subscriptions", "Insurance", "Loan EMI", "Other",
    )),
    ColumnSchema(header="Due Date", type="date"),
    ColumnSchema(header="Amount", type="currency"),
    ColumnSchema(header="Status", type="list", options=("Paid", "Pending", "Overdue")),
    ColumnSchema(header="Recurring", type="list", options=(
        "Monthly", "Quarterly", "Yearly", "One-time",
    )),
    ColumnSchema(header="Notes", type="text"),
]


def build_bills_sheet(workbook: ExcelWorkbook, style: StyleManager) -> TypedTable:
    ws = workbook.add_sheet("Bills")
    add_title_banner(ws, style, "Bills", subtitle="Blue text = your data", top_left="A2", width=7)

    table = add_typed_table(ws, style, COLUMNS, n_rows=60, table_name="Bills", top_left="A5")
    write_demo_rows(ws, style, headers=[c.header for c in COLUMNS], rows=BILLS_ROWS,
                     top_left=f"A{table.first_data_row}")

    apply_standard_protection(
        ws, editable_ranges=[f"A{table.first_data_row}:G{table.last_data_row}"]
    )
    return table
