"""Cell-level protection: unlock input cells, (re-)lock formula cells.

Every cell is locked by default (Excel's own default) — this only
matters once sheet-level protection is turned on via
`protection.sheets.protect_sheet`; locking a cell while sheet
protection is off has no visible effect in Excel.
"""

from __future__ import annotations

from openpyxl.styles import Protection

from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet


def _range(cell_range: str | CellRange) -> CellRange:
    return cell_range if isinstance(cell_range, CellRange) else CellRange.from_a1(cell_range)


def unlock_range(ws: Worksheet, cell_range: str | CellRange) -> None:
    """Mark cells as editable once sheet protection is turned on —
    typically a data table's input columns, or a Settings sheet's
    labeled-input cells.
    """
    rng = _range(cell_range)
    for row in range(rng.start.row, rng.end.row + 1):
        for col in range(rng.start.column, rng.end.column + 1):
            ws.raw.cell(row=row, column=col).protection = Protection(locked=False)


def lock_range(ws: Worksheet, cell_range: str | CellRange) -> None:
    """Explicitly (re-)lock cells. Mostly for re-locking a range that
    was previously unlocked — every cell starts locked by default.
    """
    rng = _range(cell_range)
    for row in range(rng.start.row, rng.end.row + 1):
        for col in range(rng.start.column, rng.end.column + 1):
            ws.raw.cell(row=row, column=col).protection = Protection(locked=True)
