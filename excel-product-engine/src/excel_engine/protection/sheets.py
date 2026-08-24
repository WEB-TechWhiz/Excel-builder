"""Sheet-level protection.

Turns on protection.sheet so cell-level locked/unlocked state (see
protection.cells) actually takes effect — but explicitly allows
formatting, sorting, and AutoFilter, since openpyxl's (and Excel's own)
*default* once protection is on is to block those too. Per openpyxl's
own docstring: "True values mean that protection for the object or
action is active" (i.e. blocked) — verified empirically before writing
this module, see docs/architecture.md's Phase 6 notes.

Section 16 of the original spec: "Do not make the workbook unusably
restrictive. The user must still be able to enter their own [...]
information."
"""

from __future__ import annotations

from excel_engine.core.worksheet import Worksheet


def protect_sheet(ws: Worksheet, password: str | None = None) -> None:
    """Turn on sheet protection. Only cells explicitly unlocked (see
    `protection.cells.unlock_range`) stay editable — everything else
    (locked by default) becomes read-only. Formatting, sorting, and
    AutoFilter stay allowed so the sheet doesn't become unusable.
    """
    ws.raw.protection.sheet = True
    ws.raw.protection.formatCells = False
    ws.raw.protection.formatColumns = False
    ws.raw.protection.formatRows = False
    ws.raw.protection.sort = False
    ws.raw.protection.autoFilter = False
    if password:
        ws.raw.protection.set_password(password)


def unprotect_sheet(ws: Worksheet) -> None:
    ws.raw.protection.sheet = False
