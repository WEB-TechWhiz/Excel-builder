"""Navigation bar component — a horizontal row of internal links across
the top of a sheet, pointing at other sheets in the same workbook.
"""

from __future__ import annotations

from excel_engine.core.cell import CellAddress
from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.exceptions.errors import WorkbookBuildError
from excel_engine.styles.style_manager import StyleManager


def add_navbar(
    ws: Worksheet,
    style: StyleManager,
    items: list[str],
    top_left: str | CellAddress,
    active: str | None = None,
    item_width: int = 3,
) -> CellRange:
    """Draw `items` as a row of clickable internal links (one per sheet
    name), each jumping to cell A1 of that sheet. `active`, if given, is
    rendered bold with no underline to show "you are here" rather than
    another clickable link.
    """
    if not items:
        raise WorkbookBuildError("add_navbar requires at least one item")

    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)

    for i, item in enumerate(items):
        start = anchor.offset(columns=i * item_width)
        end = start.offset(columns=item_width - 1)
        rng = CellRange(start=start, end=end)
        ws.merge(rng)
        ws.set_value(start.to_a1(), item)
        cell = ws.raw[start.to_a1()]
        cell.alignment = style.center
        if item == active:
            cell.font = style.nav_active_font
        else:
            cell.font = style.nav_link_font
            quoted = f"'{item}'" if " " in item else item
            cell.hyperlink = f"#{quoted}!A1"

    end_col = anchor.offset(columns=len(items) * item_width - 1)
    return CellRange(start=anchor, end=end_col)
