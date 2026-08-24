"""Reports sheet: summary KPI cards plus category breakdowns — section
19's "useful summaries generated from underlying data."
"""

from __future__ import annotations

from excel_engine.components import add_kpi_card, add_section_header, add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.formulas import Formula
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.formulas.financial_metrics import (
    total_expenses_formula,
    total_income_formula,
    total_investments_formula,
)

EXPENSE_CATEGORIES = (
    "Rent", "Groceries", "Utilities", "Transport", "Entertainment", "Healthcare",
    "Shopping", "Other",
)
INCOME_CATEGORIES = ("Salary", "Freelance", "Investment Returns", "Rental Income", "Gift", "Other")


def build_reports_sheet(workbook: ExcelWorkbook, style: StyleManager) -> None:
    ws = workbook.add_sheet("Reports")
    add_title_banner(ws, style, "Reports", subtitle="Auto-calculated summaries",
                      top_left="A2", width=6)

    add_kpi_card(ws, style, "Total Income (all-time)", total_income_formula(),
                 top_left="A5", number_format='"₹"#,##0')
    add_kpi_card(ws, style, "Total Expenses (all-time)", total_expenses_formula(),
                 top_left="E5", number_format='"₹"#,##0')
    add_kpi_card(ws, style, "Total Investments", total_investments_formula(),
                 top_left="I5", number_format='"₹"#,##0')

    add_section_header(ws, style, "Expenses by Category", top_left="A9", width=2)
    row = 10
    for category in EXPENSE_CATEGORIES:
        ws.set_value(f"A{row}", category)
        ws.set_formula(f"B{row}", Formula.sumifs("Expenses", "Amount", ("Category", category)))
        ws.raw[f"B{row}"].number_format = '"₹"#,##0'
        ws.raw[f"B{row}"].font = style.formula_font
        row += 1

    add_section_header(ws, style, "Income by Category", top_left="D9", width=2)
    row = 10
    for category in INCOME_CATEGORIES:
        ws.set_value(f"D{row}", category)
        ws.set_formula(f"E{row}", Formula.sumifs("Income", "Amount", ("Category", category)))
        ws.raw[f"E{row}"].number_format = '"₹"#,##0'
        ws.raw[f"E{row}"].font = style.formula_font
        row += 1
