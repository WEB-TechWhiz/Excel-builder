"""Goals sheet: Goal, Target Amount, Current Amount, Target Date,
Progress (computed), Status (computed).
"""

from __future__ import annotations

from excel_engine.components import add_progress_bar, add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.demo_data import write_demo_rows
from excel_engine.data.tables import ColumnSchema, TypedTable, add_typed_table
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.data.demo_data import GOALS_ROWS

COLUMNS = [
    ColumnSchema(header="Goal", type="text"),
    ColumnSchema(header="Target Amount", type="currency"),
    ColumnSchema(header="Current Amount", type="currency"),
    ColumnSchema(header="Target Date", type="date"),
    ColumnSchema(header="Progress", type="percent",
                 formula="{Current Amount}/{Target Amount}"),
    ColumnSchema(header="Status", type="text",
                 formula='IF({Current Amount}>={Target Amount},"Achieved",'
                         'IF({Target Date}<TODAY(),"Overdue","In Progress"))'),
]


def build_goals_sheet(workbook: ExcelWorkbook, style: StyleManager) -> TypedTable:
    ws = workbook.add_sheet("Goals")
    add_title_banner(
        ws, style, "Goals",
        subtitle="Blue text = your data · Progress and Status are auto-calculated",
        top_left="A2", width=6,
    )

    table = add_typed_table(ws, style, COLUMNS, n_rows=20, table_name="Goals", top_left="A5")
    write_demo_rows(ws, style, headers=[c.header for c in COLUMNS], rows=GOALS_ROWS,
                     top_left=f"A{table.first_data_row}")

    progress_col = table.column_letters["Progress"]
    add_progress_bar(
        ws, style, f"{progress_col}{table.first_data_row}:{progress_col}{table.last_data_row}",
        min_value=0, max_value=1,
    )

    # Goal/Target Amount/Current Amount/Target Date (A-D) are input;
    # Progress/Status (E-F) are formulas and stay locked.
    apply_standard_protection(
        ws, editable_ranges=[f"A{table.first_data_row}:D{table.last_data_row}"]
    )
    return table
