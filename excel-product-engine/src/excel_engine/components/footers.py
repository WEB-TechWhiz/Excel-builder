"""Footer component — a small caption line at the bottom of a sheet,
e.g. attribution or version text.
"""

from __future__ import annotations

from excel_engine.core.cell import CellAddress
from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_footer(
    ws: Worksheet,
    style: StyleManager,
    text: str,
    top_left: str | CellAddress,
    width: int = 10,
) -> CellRange:
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)
    end = anchor.offset(columns=width - 1)
    rng = CellRange(start=anchor, end=end)
    ws.merge(rng)
    ws.set_value(anchor.to_a1(), text)
    cell = ws.raw[anchor.to_a1()]
    cell.font = style.caption_font
    cell.alignment = style.left
    return rng
