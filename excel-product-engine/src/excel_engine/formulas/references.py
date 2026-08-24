"""Safe reference construction — table columns, sheet ranges, quoted
criteria literals, and named ranges — so formula-building code never
hand-concatenates strings that could produce a malformed formula.
"""

from __future__ import annotations

from excel_engine.core.range import CellRange


def table_column(table_name: str, column: str) -> str:
    """`Income`, `Amount` -> `Income[Amount]` — a structured reference.

    Requires `table_name` to be a real Excel Table (e.g. one created by
    `excel_engine.components.add_data_table` / `data.tables.add_typed_table`).
    Verified against this project's LibreOffice-based recalc harness —
    see docs/architecture.md.
    """
    return f"{table_name}[{column}]"


def sheet_range(sheet: str, cell_range: str | CellRange) -> str:
    """`'Orders'`, `'C2:C50'` -> `Orders!C2:C50` (quoted if the sheet
    name has a space). Delegates to `CellRange` for the quoting rule so
    it's defined in exactly one place in the whole engine.
    """
    range_obj = cell_range if isinstance(cell_range, CellRange) else CellRange.from_a1(cell_range)
    return range_obj.to_a1(sheet=sheet)


def quote_criteria(value: str) -> str:
    """Turn a Python string into a safely-quoted Excel formula literal,
    escaping embedded double quotes the way Excel expects (`"` -> `""`).
    """
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def named_range(name: str) -> str:
    """A defined name used as a formula reference — just its name, with
    no further quoting/escaping (Excel resolves it directly).
    """
    return name
