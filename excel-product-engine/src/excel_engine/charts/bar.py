"""Bar chart — category totals/averages/counts from a typed table."""

from __future__ import annotations

from openpyxl.chart import BarChart

from excel_engine.charts.manager import Agg, build_category_source_table
from excel_engine.core.cell import CellAddress
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_bar_chart(
    ws: Worksheet,
    style: StyleManager,
    title: str,
    source_table: str,
    category_column: str,
    value_column: str,
    categories: list[str],
    anchor_cell: str,
    data_top_left: str | CellAddress,
    agg: Agg = "SUM",
    width: float = 15,
    height: float = 9,
) -> None:
    """A themed column chart of `value_column` grouped by
    `category_column`, both from `source_table` (a real Excel Table —
    e.g. one created by `data.tables.add_typed_table`). The small
    aggregation table backing the chart is written at `data_top_left`
    (callers typically tuck this off to the side of the visible sheet).
    """
    source = build_category_source_table(
        ws, style, source_table, category_column, value_column, categories, agg, data_top_left
    )

    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = title
    chart.add_data(source.data_reference(ws.raw), titles_from_data=True)
    chart.set_categories(source.category_reference(ws.raw))
    chart.width, chart.height = width, height
    ws.raw.add_chart(chart, anchor_cell)
