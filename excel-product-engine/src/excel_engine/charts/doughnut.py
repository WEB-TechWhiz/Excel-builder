"""Doughnut chart — share-of-total by category, same data shape as the
pie chart, different visual (a hole in the middle, room for a center
label like a total if a caller adds one manually).
"""

from __future__ import annotations

from openpyxl.chart import DoughnutChart

from excel_engine.charts.manager import Agg, build_category_source_table
from excel_engine.core.cell import CellAddress
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_doughnut_chart(
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
    width: float = 12,
    height: float = 9,
) -> None:
    source = build_category_source_table(
        ws, style, source_table, category_column, value_column, categories, agg, data_top_left
    )

    chart = DoughnutChart()
    chart.title = title
    chart.add_data(source.data_reference(ws.raw), titles_from_data=True)
    chart.set_categories(source.category_reference(ws.raw))
    chart.width, chart.height = width, height
    ws.raw.add_chart(chart, anchor_cell)
