"""Income sheet: Date, Source, Category, Amount, Notes."""

from __future__ import annotations

from excel_engine.components import add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.data.tables import ColumnSchema, TypedTable, add_typed_table
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.data.demo_data import INCOME_ROWS

COLUMNS = [
    ColumnSchema(header="Date", type="date"),
    ColumnSchema(header="Source", type="text"),
    ColumnSchema(header="Category", type="list", options=(
        "Salary", "Freelance", "Investment Returns", "Rental Income", "Gift", "Other",
    )),
    ColumnSchema(header="Amount", type="currency"),
    ColumnSchema(header="Notes", type="text"),
]


def build_income_sheet(workbook: ExcelWorkbook, style: StyleManager) -> TypedTable:
    ws = workbook.add_sheet("Income")
    add_title_banner(ws, style, "Income", subtitle="Blue text = your data", top_left="A2", width=5)

    table = add_typed_table(ws, style, COLUMNS, n_rows=100, table_name="Income", top_left="A5")
    write_demo_rows(ws, style, headers=[c.header for c in COLUMNS], rows=INCOME_ROWS,
                     top_left=f"A{table.first_data_row}")

    apply_standard_protection(
        ws, editable_ranges=[f"A{table.first_data_row}:E{table.last_data_row}"]
    )
    return table
