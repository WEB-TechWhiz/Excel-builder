"""Line chart — a trend over the trailing N months from a typed table."""

from __future__ import annotations

from datetime import date

from openpyxl.chart import LineChart

from excel_engine.charts.manager import Agg, build_trend_source_table
from excel_engine.core.cell import CellAddress
from excel_engine.core.worksheet import Worksheet
from excel_engine.styles.style_manager import StyleManager


def add_line_chart(
    ws: Worksheet,
    style: StyleManager,
    title: str,
    source_table: str,
    date_column: str,
    value_column: str,
    anchor_cell: str,
    data_top_left: str | CellAddress,
    periods: int = 6,
    agg: Agg = "SUM",
    as_of: date | None = None,
    width: float = 15,
    height: float = 9,
) -> None:
    """A themed trend line of `value_column` over the trailing `periods`
    months, bucketed by `date_column`, both from `source_table`.

    Uses straight line segments with markers, not curve-smoothing — a
    smoothed curve would visually imply data between months that
    doesn't exist.
    """
    source = build_trend_source_table(
        ws, style, source_table, date_column, value_column, periods, agg, data_top_left, as_of
    )

    chart = LineChart()
    chart.title = title
    chart.style = 12
    chart.add_data(source.data_reference(ws.raw), titles_from_data=True)
    chart.set_categories(source.category_reference(ws.raw))
    for series in chart.series:
        series.smooth = False
        series.marker.symbol = "circle"
    chart.width, chart.height = width, height
    ws.raw.add_chart(chart, anchor_cell)
