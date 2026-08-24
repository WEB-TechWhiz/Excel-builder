"""Single button component — a filled, bordered, centered-text cell,
optionally an internal hyperlink to another sheet. The primitive that
`navbar` composes into a row, and reusable anywhere a sheet needs one
call-to-action (e.g. "Add New Entry", "Back to Dashboard").
"""

from __future__ import annotations

from excel_engine.core.cell import CellAddress
from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_button(
    ws: Worksheet,
    style: StyleManager,
    label: str,
    top_left: str | CellAddress,
    target_sheet: str | None = None,
    target_cell: str = "A1",
    width: int = 3,
) -> CellRange:
    """Draw a single filled 'button' cell. If `target_sheet` is given,
    clicking it jumps to `target_cell` on that sheet.
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)
    end = anchor.offset(columns=width - 1)
    rng = CellRange(start=anchor, end=end)
    ws.merge(rng)

    ws.set_value(anchor.to_a1(), label)
    cell = ws.raw[anchor.to_a1()]
    cell.font = style.header_font
    cell.fill = style.header_fill
    cell.alignment = style.center
    cell.border = style.thin_border

    if target_sheet is not None:
        quoted = f"'{target_sheet}'" if " " in target_sheet else target_sheet
        cell.hyperlink = f"#{quoted}!{target_cell}"

    return rng
