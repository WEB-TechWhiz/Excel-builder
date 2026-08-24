"""Shared chart-building plumbing.

Excel charts need a small, already-aggregated data range to read from —
this module builds that (a "Category | Value" or "Period | Value"
helper table, driven by real SUMIFS/AVERAGEIFS/COUNTIFS formulas via
the Phase 5 formula engine) and hands back a `ChartSourceTable` that
knows how to turn itself into openpyxl `Reference` objects. The
per-type modules (bar/line/pie/doughnut) call into this rather than
duplicating table-building logic — see section 12/35 of the original
spec: "Charts must be generated through the chart engine, not
duplicated across products."
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Literal

from excel_engine.core.cell import CellAddress
from excel_engine.formulas import Formula
from excel_engine.formulas import functions as fn
from excel_engine.formulas import references as ref
from excel_engine.styles.style_manager import StyleManager

if TYPE_CHECKING:
    from openpyxl.chart import Reference
    from openpyxl.worksheet.worksheet import Worksheet as OpenpyxlWorksheet

    from excel_engine.core.worksheet import Worksheet

Agg = Literal["SUM", "AVERAGE", "COUNT"]


@dataclass(frozen=True, slots=True)
class ChartSourceTable:
    """A small Category|Value (or Period|Value) helper table already
    written to a sheet, self-sufficient to build the two `Reference`
    objects any openpyxl chart needs.
    """

    category_col: int
    value_col: int
    header_row: int
    first_data_row: int
    last_data_row: int

    def data_reference(self, raw_ws: OpenpyxlWorksheet) -> Reference:
        from openpyxl.chart import Reference as _Reference

        return _Reference(
            raw_ws, min_col=self.value_col, min_row=self.header_row, max_row=self.last_data_row
        )

    def category_reference(self, raw_ws: OpenpyxlWorksheet) -> Reference:
        from openpyxl.chart import Reference as _Reference

        return _Reference(
            raw_ws, min_col=self.category_col, min_row=self.first_data_row,
            max_row=self.last_data_row,
        )


def months_back(anchor_date: date, n: int) -> list[tuple[int, int]]:
    """List of (year, month) tuples, n months ending at anchor_date's
    month, oldest first. Public — reused by product code that needs its
    own month-bucketed formulas beyond the single-source-table charts
    this module builds (e.g. a multi-series cash-flow chart).
    """
    out = []
    y, m = anchor_date.year, anchor_date.month
    for i in range(n - 1, -1, -1):
        mm, yy = m - i, y
        while mm <= 0:
            mm += 12
            yy -= 1
        out.append((yy, mm))
    return out


def build_category_source_table(
    ws: Worksheet,
    style: StyleManager,
    source_table: str,
    category_column: str,
    value_column: str,
    categories: list[str],
    agg: Agg,
    top_left: str | CellAddress,
) -> ChartSourceTable:
    """Write `Category | Value` with one SUMIFS/AVERAGEIFS/COUNTIFS
    formula per category (via structured references into `source_table`)
    — used by bar/pie/doughnut charts. `categories` must be given
    explicitly (no UNIQUE() — see docs/architecture.md's Phase 2 notes
    on formula compatibility).
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)

    ws.set_value(anchor.to_a1(), category_column)
    ws.raw[anchor.to_a1()].font = style.caption_font
    value_header = anchor.offset(columns=1)
    ws.set_value(value_header.to_a1(), value_column)
    ws.raw[value_header.to_a1()].font = style.caption_font

    for i, category in enumerate(categories):
        row_addr = anchor.offset(rows=1 + i)
        ws.set_value(row_addr.to_a1(), category)
        ws.raw[row_addr.to_a1()].font = style.caption_font

        value_addr = row_addr.offset(columns=1)
        criteria = (category_column, category)
        if agg == "COUNT":
            formula = Formula.countifs(source_table, criteria)
        elif agg == "AVERAGE":
            formula = Formula.averageifs(source_table, value_column, criteria)
        else:
            formula = Formula.sumifs(source_table, value_column, criteria)
        ws.set_formula(value_addr.to_a1(), formula)
        ws.raw[value_addr.to_a1()].font = style.caption_font

    return ChartSourceTable(
        category_col=anchor.column,
        value_col=value_header.column,
        header_row=anchor.row,
        first_data_row=anchor.row + 1,
        last_data_row=anchor.row + len(categories),
    )


def build_trend_source_table(
    ws: Worksheet,
    style: StyleManager,
    source_table: str,
    date_column: str,
    value_column: str,
    periods: int,
    agg: Agg,
    top_left: str | CellAddress,
    as_of: date | None = None,
) -> ChartSourceTable:
    """Write `Period | Value` — one row per trailing month, each a
    SUMIFS/AVERAGEIFS/COUNTIFS with a `DATE(...)` range criterion — used
    by line charts. Uses the low-level `formulas.functions` builders
    directly (not `Formula.sumifs`) since date-range criteria are
    formula fragments, not literal strings to quote.
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)
    months = months_back(as_of or date.today(), periods)

    ws.set_value(anchor.to_a1(), "Period")
    ws.raw[anchor.to_a1()].font = style.caption_font
    value_header = anchor.offset(columns=1)
    ws.set_value(value_header.to_a1(), value_column)
    ws.raw[value_header.to_a1()].font = style.caption_font

    date_ref = ref.table_column(source_table, date_column)
    value_ref = ref.table_column(source_table, value_column)

    for i, (yy, mm) in enumerate(months):
        row_addr = anchor.offset(rows=1 + i)
        ws.set_value(row_addr.to_a1(), f"{calendar.month_abbr[mm]} {yy}")
        ws.raw[row_addr.to_a1()].font = style.caption_font

        start = f"DATE({yy},{mm},1)"
        end = f"DATE({yy + 1},1,1)" if mm == 12 else f"DATE({yy},{mm + 1},1)"
        criteria = ((date_ref, f'">="&{start}'), (date_ref, f'"<"&{end}'))

        value_addr = row_addr.offset(columns=1)
        if agg == "COUNT":
            formula = fn.countifs(*criteria)
        elif agg == "AVERAGE":
            formula = fn.averageifs(value_ref, *criteria)
        else:
            formula = fn.sumifs(value_ref, *criteria)
        ws.set_formula(value_addr.to_a1(), formula)
        ws.raw[value_addr.to_a1()].font = style.caption_font

    return ChartSourceTable(
        category_col=anchor.column,
        value_col=value_header.column,
        header_row=anchor.row,
        first_data_row=anchor.row + 1,
        last_data_row=anchor.row + len(months),
    )
