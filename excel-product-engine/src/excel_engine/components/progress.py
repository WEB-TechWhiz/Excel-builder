"""Progress indicator component — a conditional-format data bar over a
cell or range holding a value between `min_value` and `max_value`
(e.g. a goal's 0..1 completion fraction, or a formula that computes one).
"""

from __future__ import annotations

from openpyxl.formatting.rule import DataBarRule

from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_progress_bar(
    ws: Worksheet,
    style: StyleManager,
    cell_range: str | CellRange,
    min_value: float = 0,
    max_value: float = 1,
) -> None:
    """Apply a themed data bar to `cell_range`. Each cell in the range
    should hold, or compute via formula, a number between `min_value`
    and `max_value`.
    """
    ref = cell_range.to_a1() if isinstance(cell_range, CellRange) else cell_range
    rule = DataBarRule(
        start_type="num",
        start_value=min_value,
        end_type="num",
        end_value=max_value,
        color=style.palette.primary,
    )
    ws.raw.conditional_formatting.add(ref, rule)
