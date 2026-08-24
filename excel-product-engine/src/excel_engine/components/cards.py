"""KPI card component — a small, theme-styled 'stat card' (label + big
formula-driven value) that dashboards stack in a grid.
"""

from __future__ import annotations

from excel_engine.core.cell import CellAddress
from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_kpi_card(
    ws: Worksheet,
    style: StyleManager,
    label: str,
    formula: str,
    top_left: str | CellAddress,
    number_format: str = "General",
    width: int = 3,
) -> CellRange:
    """Draw a KPI card: a label row + a two-row-tall formula-driven value
    block beneath it.

    `formula` must be a full Excel formula string starting with '='
    (Phase 5's formula engine will build these safely; for now callers
    pass a raw string). Returns the CellRange the whole card occupies,
    so callers can lay out a grid of cards without recomputing positions.
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)

    label_range = CellRange(start=anchor, end=anchor.offset(columns=width - 1))
    ws.merge(label_range)
    ws.set_value(anchor.to_a1(), label.upper())
    label_cell = ws.raw[anchor.to_a1()]
    label_cell.font = style.kpi_label_font
    label_cell.fill = style.card_fill
    label_cell.alignment = style.center

    value_anchor = anchor.offset(rows=1)
    value_end = value_anchor.offset(rows=1, columns=width - 1)
    value_range = CellRange(start=value_anchor, end=value_end)
    ws.merge(value_range)
    ws.set_formula(value_anchor.to_a1(), formula)
    value_cell = ws.raw[value_anchor.to_a1()]
    value_cell.font = style.kpi_value_font
    value_cell.fill = style.card_fill
    value_cell.alignment = style.center
    value_cell.number_format = number_format

    full_range = CellRange(start=anchor, end=value_end)
    for row in range(full_range.start.row, full_range.end.row + 1):
        for col in range(full_range.start.column, full_range.end.column + 1):
            ws.raw.cell(row=row, column=col).border = style.thin_border

    return full_range
