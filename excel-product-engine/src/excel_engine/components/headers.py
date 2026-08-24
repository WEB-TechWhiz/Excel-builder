"""Title banner and section header components."""

from __future__ import annotations

from excel_engine.core.cell import CellAddress
from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_title_banner(
    ws: Worksheet,
    style: StyleManager,
    title: str,
    subtitle: str | None = None,
    top_left: str | CellAddress = "A1",
    width: int = 10,
) -> CellRange:
    """A full-width title banner at the top of a sheet, optionally with a
    smaller subtitle line directly beneath it (e.g. "Blue = your data").
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)

    title_end = anchor.offset(columns=width - 1)
    title_range = CellRange(start=anchor, end=title_end)
    ws.merge(title_range)
    ws.set_value(anchor.to_a1(), title)
    title_cell = ws.raw[anchor.to_a1()]
    title_cell.font = style.title_font
    title_cell.fill = style.header_fill
    title_cell.alignment = style.left

    if subtitle is None:
        return title_range

    sub_anchor = anchor.offset(rows=1)
    sub_end = sub_anchor.offset(columns=width - 1)
    sub_range = CellRange(start=sub_anchor, end=sub_end)
    ws.merge(sub_range)
    ws.set_value(sub_anchor.to_a1(), subtitle)
    sub_cell = ws.raw[sub_anchor.to_a1()]
    sub_cell.font = style.subtitle_font
    sub_cell.fill = style.header_fill
    sub_cell.alignment = style.left

    return CellRange(start=anchor, end=sub_end)


def add_section_header(
    ws: Worksheet,
    style: StyleManager,
    text: str,
    top_left: str | CellAddress,
    width: int = 4,
) -> CellRange:
    """A smaller, in-sheet header for labeling a sub-section (e.g. a
    helper table). Uses subheading styling, not the full title banner.
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)
    end = anchor.offset(columns=width - 1)
    rng = CellRange(start=anchor, end=end)
    ws.merge(rng)
    ws.set_value(anchor.to_a1(), text)
    cell = ws.raw[anchor.to_a1()]
    cell.font = style.subheading_font
    cell.alignment = style.left
    return rng
