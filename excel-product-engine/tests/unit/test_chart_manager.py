from excel_engine.charts.manager import build_category_source_table, build_trend_source_table
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.data.tables import ColumnSchema, add_typed_table
from excel_engine.styles.style_manager import StyleManager


def _orders_sheet(wb: ExcelWorkbook, style: StyleManager):
    ws = wb.add_sheet("Orders")
    columns = [
        ColumnSchema(header="Date", type="date"),
        ColumnSchema(header="Colorway", type="list", options=("Amber", "Teal")),
        ColumnSchema(header="Amount", type="currency"),
    ]
    add_typed_table(ws, style, columns, n_rows=20, table_name="Orders")
    return ws


def test_category_source_table_structure():
    wb = ExcelWorkbook()
    style = StyleManager.for_theme("premium")
    ws = _orders_sheet(wb, style)

    source = build_category_source_table(
        ws, style, "Orders", "Colorway", "Amount", ["Amber", "Teal"], "SUM", top_left="T5"
    )
    assert ws.get_value("T5") == "Colorway"
    assert ws.get_value("U5") == "Amount"
    assert ws.get_value("T6") == "Amber"
    assert ws.get_value("U6") == '=SUMIFS(Orders[Amount], Orders[Colorway], "Amber")'
    assert source.first_data_row == 6
    assert source.last_data_row == 7


def test_category_source_table_average_agg():
    wb = ExcelWorkbook()
    style = StyleManager.for_theme("premium")
    ws = _orders_sheet(wb, style)
    build_category_source_table(
        ws, style, "Orders", "Colorway", "Amount", ["Amber"], "AVERAGE", top_left="T5"
    )
    assert ws.get_value("U6") == '=IFERROR(AVERAGEIFS(Orders[Amount], Orders[Colorway], "Amber"), 0)'


def test_category_source_table_count_agg():
    wb = ExcelWorkbook()
    style = StyleManager.for_theme("premium")
    ws = _orders_sheet(wb, style)
    build_category_source_table(
        ws, style, "Orders", "Colorway", "Amount", ["Amber"], "COUNT", top_left="T5"
    )
    assert ws.get_value("U6") == '=COUNTIFS(Orders[Colorway], "Amber")'


def test_trend_source_table_structure():
    from datetime import date

    wb = ExcelWorkbook()
    style = StyleManager.for_theme("premium")
    ws = _orders_sheet(wb, style)

    source = build_trend_source_table(
        ws, style, "Orders", "Date", "Amount", periods=3, agg="SUM",
        top_left="T5", as_of=date(2026, 8, 15),
    )
    assert ws.get_value("T5") == "Period"
    assert ws.get_value("U5") == "Amount"
    assert ws.get_value("T6") == "Jun 2026"
    assert ws.get_value("T7") == "Jul 2026"
    assert ws.get_value("T8") == "Aug 2026"
    formula = ws.get_value("U8")
    assert "DATE(2026,8,1)" in formula
    assert "DATE(2026,9,1)" in formula
    assert source.first_data_row == 6
    assert source.last_data_row == 8
