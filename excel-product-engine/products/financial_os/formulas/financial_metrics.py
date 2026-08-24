"""Financial-OS-specific formulas.

What "Net Worth" or "Savings Rate" *means* lives here — never in the
generic engine (section 2.2: "Do not mix Financial OS business logic
into generic engine components"). Every formula is still built through
`excel_engine.formulas`, never hand-concatenated.
"""

from __future__ import annotations

from excel_engine.formulas import Formula
from excel_engine.formulas import functions as fn
from excel_engine.formulas import references as ref

_THIS_MONTH_START = "DATE(YEAR(TODAY()),MONTH(TODAY()),1)"
_THIS_MONTH_END = "EOMONTH(TODAY(),0)+1"


def _this_month_sumifs(table: str, value_column: str, date_column: str) -> str:
    """SUMIFS bounded to the current calendar month, evaluated fresh
    every time the workbook opens (TODAY()-driven, not a snapshot).
    """
    date_ref = ref.table_column(table, date_column)
    value_ref = ref.table_column(table, value_column)
    criteria = (
        (date_ref, f'">="&{_THIS_MONTH_START}'),
        (date_ref, f'"<"&{_THIS_MONTH_END}'),
    )
    return fn.sumifs(value_ref, *criteria)


def _latest_net_worth_snapshot_sumifs(type_value: str) -> str:
    """Net Worth is a point-in-time snapshot, not a running total — sum
    only the rows dated on the most recent date present in the sheet,
    not every historical entry ever logged (that's what the Net Worth
    Trend chart is for). Verified empirically: SUMIFS accepts a bare
    MAX(...) sub-formula as an exact-match criteria value.
    """
    value_ref = ref.table_column("NetWorth", "Value")
    type_ref = ref.table_column("NetWorth", "Type")
    date_ref = ref.table_column("NetWorth", "Date")
    criteria = (
        (type_ref, ref.quote_criteria(type_value)),
        (date_ref, f"MAX({date_ref})"),
    )
    return fn.sumifs(value_ref, *criteria)


def total_assets_formula() -> str:
    return _latest_net_worth_snapshot_sumifs("Asset")


def total_liabilities_formula() -> str:
    return _latest_net_worth_snapshot_sumifs("Liability")


def net_worth_formula(assets_cell: str, liabilities_cell: str) -> str:
    return f"={assets_cell}-{liabilities_cell}"


def monthly_income_formula() -> str:
    return _this_month_sumifs("Income", "Amount", "Date")


def monthly_expenses_formula() -> str:
    return _this_month_sumifs("Expenses", "Amount", "Date")


def savings_formula(income_cell: str, expenses_cell: str) -> str:
    return f"={income_cell}-{expenses_cell}"


def savings_rate_formula(savings_cell: str, income_cell: str) -> str:
    return Formula.percentage_of_total(savings_cell, income_cell)


def total_investments_formula() -> str:
    return Formula.sum("Investments", "Current Value")


def total_debt_formula() -> str:
    return total_liabilities_formula()


def total_income_formula() -> str:
    """All-time total (used on the Reports sheet, distinct from the
    Dashboard's current-month figure).
    """
    return Formula.sum("Income", "Amount")


def total_expenses_formula() -> str:
    return Formula.sum("Expenses", "Amount")
