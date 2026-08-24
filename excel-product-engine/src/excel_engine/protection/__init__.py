"""Protection engine — cell-level lock/unlock plus sheet-level
protection, composed into one common workflow: protect a sheet while
keeping specific ranges editable.

    from excel_engine.protection import apply_standard_protection
    apply_standard_protection(orders_sheet, editable_ranges=["A2:C51"])
"""

from __future__ import annotations

from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.protection.cells import lock_range, unlock_range
from excel_engine.protection.sheets import protect_sheet, unprotect_sheet


def apply_standard_protection(
    ws: Worksheet,
    editable_ranges: list[str | CellRange],
    password: str | None = None,
) -> None:
    """Unlock `editable_ranges` (typically a table's input columns),
    leave everything else at its default-locked state, then turn on
    sheet protection without disabling formatting/sorting/AutoFilter.
    """
    for cell_range in editable_ranges:
        unlock_range(ws, cell_range)
    protect_sheet(ws, password=password)


__all__ = [
    "apply_standard_protection",
    "lock_range",
    "unlock_range",
    "protect_sheet",
    "unprotect_sheet",
]
