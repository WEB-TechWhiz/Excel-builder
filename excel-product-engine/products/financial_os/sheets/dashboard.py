"""Financial OS Dashboard: KPI cards (Net Worth, Monthly Income,
Monthly Expenses, Savings, Savings Rate, Investments, Debt), four
charts (Monthly Cash Flow, Expense Breakdown, Investment Allocation,
Net Worth Trend), and a short Goals progress summary.

Two of the four charts (Cash Flow, Net Worth Trend) need a second data
series or a cross-table net calculation that the generic single-table
chart engine (Phase 6) doesn't cover — those are built directly here
with openpyxl, reaching into `.raw` the same way the engine's own
components do internally when a generic abstraction doesn't fit yet
(see docs/architecture.md's Phase 8 notes).
"""

from __future__ import annotations

import calendar
from datetime import date

from openpyxl.chart import LineChart, Reference

from excel_engine.charts import add_doughnut_chart, add_pie_chart
from excel_engine.charts.manager import months_back
from excel_engine.components import (
    add_kpi_card,
    add_progress_bar,
    add_section_header,
    add_title_banner,
)
from excel_engine.core.cell import CellAddress
from excel_engine.core.range import CellRange
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.core.worksheet import Worksheet
from excel_engine.data.tables import TypedTable
from excel_engine.formulas import functions as fn
from excel_engine.formulas import references as ref
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.formulas import financial_metrics as fm

EXPENSE_CATEGORIES = (
    "Rent", "Groceries", "Utilities", "Transport", "Entertainment", "Healthcare",
    "Shopping", "Other",
)
INVESTMENT_ASSET_TYPES = (
    "Mutual Fund", "Stock", "Fixed Deposit", "PPF", "Emergency Fund",
    "Gold", "Real Estate", "Other",
)


def _build_cash_flow_chart(
    ws: Worksheet, style: StyleManager, anchor_cell: str, data_top_left: str, periods: int = 3,
    as_of: date | None = None,
) -> None:
    """A 2-series line chart: Income vs. Expenses per trailing month."""
    anchor = CellAddress.from_a1(data_top_left)
    months = months_back(as_of or date.today(), periods)

    ws.set_value(anchor.to_a1(), "Period")
    ws.raw[anchor.to_a1()].font = style.caption_font
    income_header = anchor.offset(columns=1)
    ws.set_value(income_header.to_a1(), "Income")
    ws.raw[income_header.to_a1()].font = style.caption_font
    expense_header = anchor.offset(columns=2)
    ws.set_value(expense_header.to_a1(), "Expenses")
    ws.raw[expense_header.to_a1()].font = style.caption_font

    income_date_ref = ref.table_column("Income", "Date")
    income_amount_ref = ref.table_column("Income", "Amount")
    expense_date_ref = ref.table_column("Expenses", "Date")
    expense_amount_ref = ref.table_column("Expenses", "Amount")

    for i, (yy, mm) in enumerate(months):
        row_addr = anchor.offset(rows=1 + i)
        ws.set_value(row_addr.to_a1(), f"{calendar.month_abbr[mm]} {yy}")
        ws.raw[row_addr.to_a1()].font = style.caption_font

        start = f"DATE({yy},{mm},1)"
        end = f"DATE({yy + 1},1,1)" if mm == 12 else f"DATE({yy},{mm + 1},1)"

        income_cell = row_addr.offset(columns=1)
        income_formula = fn.sumifs(
            income_amount_ref,
            (income_date_ref, f'">="&{start}'), (income_date_ref, f'"<"&{end}'),
        )
        ws.set_formula(income_cell.to_a1(), income_formula)
        ws.raw[income_cell.to_a1()].font = style.caption_font

        expense_cell = row_addr.offset(columns=2)
        expense_formula = fn.sumifs(
            expense_amount_ref,
            (expense_date_ref, f'">="&{start}'), (expense_date_ref, f'"<"&{end}'),
        )
        ws.set_formula(expense_cell.to_a1(), expense_formula)
        ws.raw[expense_cell.to_a1()].font = style.caption_font

    last_row = anchor.row + len(months)
    chart = LineChart()
    chart.title = "Monthly Cash Flow"
    chart.style = 12
    data_ref = Reference(ws.raw, min_col=income_header.column, max_col=expense_header.column,
                          min_row=anchor.row, max_row=last_row)
    cat_ref = Reference(ws.raw, min_col=anchor.column, min_row=anchor.row + 1, max_row=last_row)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cat_ref)
    for series in chart.series:
        series.smooth = False
        series.marker.symbol = "circle"
    chart.width, chart.height = 15, 9
    ws.raw.add_chart(chart, anchor_cell)


def _build_net_worth_trend_chart(
    ws: Worksheet, style: StyleManager, anchor_cell: str, data_top_left: str, periods: int = 3,
    as_of: date | None = None,
) -> None:
    """A 1-series line chart: (Assets - Liabilities) per trailing month,
    from the dated Net Worth log.
    """
    anchor = CellAddress.from_a1(data_top_left)
    months = months_back(as_of or date.today(), periods)

    ws.set_value(anchor.to_a1(), "Period")
    ws.raw[anchor.to_a1()].font = style.caption_font
    net_header = anchor.offset(columns=1)
    ws.set_value(net_header.to_a1(), "Net Worth")
    ws.raw[net_header.to_a1()].font = style.caption_font

    date_ref = ref.table_column("NetWorth", "Date")
    value_ref = ref.table_column("NetWorth", "Value")
    type_ref = ref.table_column("NetWorth", "Type")

    for i, (yy, mm) in enumerate(months):
        row_addr = anchor.offset(rows=1 + i)
        ws.set_value(row_addr.to_a1(), f"{calendar.month_abbr[mm]} {yy}")
        ws.raw[row_addr.to_a1()].font = style.caption_font

        start = f"DATE({yy},{mm},1)"
        end = f"DATE({yy + 1},1,1)" if mm == 12 else f"DATE({yy},{mm + 1},1)"
        date_criteria = ((date_ref, f'">="&{start}'), (date_ref, f'"<"&{end}'))

        assets = fn.sumifs(value_ref, (type_ref, '"Asset"'), *date_criteria)
        liabilities = fn.sumifs(value_ref, (type_ref, '"Liability"'), *date_criteria)

        net_cell = row_addr.offset(columns=1)
        ws.set_formula(net_cell.to_a1(), f"={assets[1:]}-{liabilities[1:]}")
        ws.raw[net_cell.to_a1()].font = style.caption_font

    last_row = anchor.row + len(months)
    chart = LineChart()
    chart.title = "Net Worth Trend"
    chart.style = 12
    data_ref = Reference(ws.raw, min_col=net_header.column, min_row=anchor.row, max_row=last_row)
    cat_ref = Reference(ws.raw, min_col=anchor.column, min_row=anchor.row + 1, max_row=last_row)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cat_ref)
    for series in chart.series:
        series.smooth = False
        series.marker.symbol = "circle"
    chart.width, chart.height = 15, 9
    ws.raw.add_chart(chart, anchor_cell)


def _build_goals_progress_summary(ws: Worksheet, style: StyleManager, goals_table: TypedTable, top_left: str, n: int = 3) -> None:
    anchor = CellAddress.from_a1(top_left)
    add_section_header(ws, style, "Goals Progress", top_left=anchor.to_a1(), width=4)

    goal_col = goals_table.column_letters["Goal"]
    progress_col = goals_table.column_letters["Progress"]

    for i in range(n):
        source_row = goals_table.first_data_row + i
        label_addr = anchor.offset(rows=1 + i)
        ws.set_formula(label_addr.to_a1(), f"='{goals_table.sheet_name}'!{goal_col}{source_row}")
        ws.raw[label_addr.to_a1()].font = style.body_font

        value_addr = label_addr.offset(columns=2)
        ws.set_formula(value_addr.to_a1(), f"='{goals_table.sheet_name}'!{progress_col}{source_row}")
        ws.raw[value_addr.to_a1()].number_format = "0.0%"
        ws.raw[value_addr.to_a1()].font = style.formula_font

    progress_range = CellRange(
        start=anchor.offset(rows=1, columns=2), end=anchor.offset(rows=n, columns=2)
    )
    add_progress_bar(ws, style, progress_range.to_a1())


def build_dashboard_sheet(
    workbook: ExcelWorkbook, style: StyleManager, goals_table: TypedTable
) -> None:
    ws = workbook.add_sheet("Dashboard")
    add_title_banner(ws, style, "Financial OS", subtitle="Auto-calculated", top_left="A2", width=16)

    # -- hidden helper cells (Assets/Liabilities feed the Net Worth card) --
    # Row 1 is reserved workbook-wide for the navbar (added later, in
    # product.py) — anything placed there gets clobbered by whichever
    # nav item's merge lands on these columns. Row 3+ is safe.
    ws.set_value("T3", "Total Assets")
    ws.set_formula("U3", fm.total_assets_formula())
    ws.set_value("T4", "Total Liabilities")
    ws.set_formula("U4", fm.total_liabilities_formula())
    for addr in ("T3", "T4"):
        ws.raw[addr].font = style.caption_font

    # -- KPI grid: 4 across, 2 rows (7 KPIs) --
    add_kpi_card(ws, style, "Net Worth", fm.net_worth_formula("U3", "U4"),
                 top_left="A5", number_format='"₹"#,##0')
    add_kpi_card(ws, style, "Monthly Income", fm.monthly_income_formula(),
                 top_left="E5", number_format='"₹"#,##0')
    add_kpi_card(ws, style, "Monthly Expenses", fm.monthly_expenses_formula(),
                 top_left="I5", number_format='"₹"#,##0')
    add_kpi_card(ws, style, "Savings", fm.savings_formula("E6", "I6"),
                 top_left="M5", number_format='"₹"#,##0')

    add_kpi_card(ws, style, "Savings Rate", fm.savings_rate_formula("M6", "E6"),
                 top_left="A9", number_format="0.0%")
    add_kpi_card(ws, style, "Investments", fm.total_investments_formula(),
                 top_left="E9", number_format='"₹"#,##0')
    add_kpi_card(ws, style, "Debt", fm.total_debt_formula(),
                 top_left="I9", number_format='"₹"#,##0')

    # -- charts: 2x2 grid --
    _build_cash_flow_chart(ws, style, anchor_cell="B14", data_top_left="T5")
    add_pie_chart(
        ws, style, "Expense Breakdown", "Expenses", "Category", "Amount",
        list(EXPENSE_CATEGORIES), anchor_cell="K14", data_top_left="T11",
    )
    add_doughnut_chart(
        ws, style, "Investment Allocation", "Investments", "Asset Type", "Current Value",
        list(INVESTMENT_ASSET_TYPES), anchor_cell="B32", data_top_left="T21",
    )
    _build_net_worth_trend_chart(ws, style, anchor_cell="K32", data_top_left="T31")

    # -- goals progress summary --
    _build_goals_progress_summary(ws, style, goals_table, top_left="B50")

    ws.show_gridlines(False)
