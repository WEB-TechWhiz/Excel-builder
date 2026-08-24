"""Labeled input row component — a 'Label: [value]' pattern for settings
or single-value entry sheets.
"""

from __future__ import annotations

from typing import Any

from excel_engine.core.cell import CellAddress
from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_labeled_input(
    ws: Worksheet,
    style: StyleManager,
    label: str,
    top_left: str | CellAddress,
    default_value: Any = None,
    label_width: int = 2,
    input_width: int = 2,
) -> CellRange:
    """A single row: a label cell followed by an editable-looking input
    cell (blue input font, bordered), pre-filled with `default_value`
    if given.
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)

    label_end = anchor.offset(columns=label_width - 1)
    label_range = CellRange(start=anchor, end=label_end)
    ws.merge(label_range)
    ws.set_value(anchor.to_a1(), label)
    label_cell = ws.raw[anchor.to_a1()]
    label_cell.font = style.body_font
    label_cell.alignment = style.left

    input_anchor = label_end.offset(columns=1)
    input_end = input_anchor.offset(columns=input_width - 1)
    input_range = CellRange(start=input_anchor, end=input_end)
    ws.merge(input_range)
    if default_value is not None:
        ws.set_value(input_anchor.to_a1(), default_value)
    input_cell = ws.raw[input_anchor.to_a1()]
    input_cell.font = style.input_font
    input_cell.border = style.thin_border
    input_cell.alignment = style.left

    return CellRange(start=anchor, end=input_end)
