"""Chart engine — bar/line/pie/doughnut, each backed by a small,
formula-driven aggregation table (see `charts.manager`) rather than a
static snapshot, so charts stay correct as data changes.

    from excel_engine.charts import add_bar_chart, add_line_chart
"""

from excel_engine.charts.bar import add_bar_chart
from excel_engine.charts.doughnut import add_doughnut_chart
from excel_engine.charts.line import add_line_chart
from excel_engine.charts.pie import add_pie_chart

__all__ = ["add_bar_chart", "add_line_chart", "add_pie_chart", "add_doughnut_chart"]
