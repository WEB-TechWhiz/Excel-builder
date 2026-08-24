"""Investments sheet: Date, Asset, Asset Type, Quantity, Purchase Price,
Current Value, Gain/Loss (computed).
"""

from __future__ import annotations

from excel_engine.components import add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.data.tables import ColumnSchema, TypedTable, add_typed_table
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.data.demo_data import INVESTMENT_ROWS

COLUMNS = [
    ColumnSchema(header="Date", type="date"),
    ColumnSchema(header="Asset", type="text"),
    ColumnSchema(header="Asset Type", type="list", options=(
        "Mutual Fund", "Stock", "Fixed Deposit", "PPF", "Emergency Fund",
        "Gold", "Real Estate", "Other",
    )),
    ColumnSchema(header="Quantity", type="number"),
    ColumnSchema(header="Purchase Price", type="currency"),
    ColumnSchema(header="Current Value", type="currency"),
    ColumnSchema(header="Gain/Loss", type="currency",
                 formula="{Current Value}-{Quantity}*{Purchase Price}"),
]


def build_investments_sheet(workbook: ExcelWorkbook, style: StyleManager) -> TypedTable:
    ws = workbook.add_sheet("Investments")
    add_title_banner(ws, style, "Investments",
                      subtitle="Blue text = your data · Gain/Loss is auto-calculated",
                      top_left="A2", width=7)

    table = add_typed_table(ws, style, COLUMNS, n_rows=50, table_name="Investments", top_left="A5")
    write_demo_rows(ws, style, headers=[c.header for c in COLUMNS], rows=INVESTMENT_ROWS,
                     top_left=f"A{table.first_data_row}")

    # Columns A-F are input; G (Gain/Loss) is a formula and stays locked.
    apply_standard_protection(
        ws, editable_ranges=[f"A{table.first_data_row}:F{table.last_data_row}"]
    )
    return table
