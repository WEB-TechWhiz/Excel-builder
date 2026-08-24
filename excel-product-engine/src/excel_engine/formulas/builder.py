"""The Formula builder — the single place product/component code builds
formula strings, instead of hand-concatenating Excel syntax throughout
the codebase.

    Formula.sum("Income", "Amount")              -> "=SUM(Income[Amount])"
    Formula.sum_range("Orders", "C2:C50")          -> "=SUM(Orders!C2:C50)"
    Formula.sumifs("Orders", "Amount", ("Colorway", "Saddle Amber"))
        -> '=SUMIFS(Orders[Amount], Orders[Colorway], "Saddle Amber")'

The `table`-based methods build structured references and require
`table` to be a real Excel Table (e.g. via
`excel_engine.data.tables.add_typed_table`). The `_range` methods are
the plain-A1 fallback for when there's no Table object.
"""

from __future__ import annotations

from excel_engine.formulas import functions as fn
from excel_engine.formulas import references as ref


class Formula:
    """Namespace of formula builders — never instantiated, call as
    `Formula.sum(...)`, `Formula.sumifs(...)`, etc.
    """

    # -- table-backed (structured references) --------------------------
    @staticmethod
    def sum(table: str, column: str) -> str:
        return fn.sum_(ref.table_column(table, column))

    @staticmethod
    def average(table: str, column: str, safe: bool = True) -> str:
        return fn.average(ref.table_column(table, column), safe=safe)

    @staticmethod
    def count(table: str, column: str) -> str:
        return fn.count(ref.table_column(table, column))

    @staticmethod
    def counta(table: str, column: str) -> str:
        return fn.counta(ref.table_column(table, column))

    @staticmethod
    def max(table: str, column: str, safe: bool = True) -> str:
        return fn.max_(ref.table_column(table, column), safe=safe)

    @staticmethod
    def min(table: str, column: str, safe: bool = True) -> str:
        return fn.min_(ref.table_column(table, column), safe=safe)

    @staticmethod
    def sumifs(table: str, sum_column: str, *criteria: tuple[str, str]) -> str:
        """criteria: (criteria_column, literal_value) pairs."""
        pairs = tuple(
            (ref.table_column(table, crit_col), ref.quote_criteria(value))
            for crit_col, value in criteria
        )
        return fn.sumifs(ref.table_column(table, sum_column), *pairs)

    @staticmethod
    def averageifs(
        table: str, avg_column: str, *criteria: tuple[str, str], safe: bool = True
    ) -> str:
        pairs = tuple(
            (ref.table_column(table, crit_col), ref.quote_criteria(value))
            for crit_col, value in criteria
        )
        return fn.averageifs(ref.table_column(table, avg_column), *pairs, safe=safe)

    @staticmethod
    def countifs(table: str, *criteria: tuple[str, str]) -> str:
        pairs = tuple(
            (ref.table_column(table, crit_col), ref.quote_criteria(value))
            for crit_col, value in criteria
        )
        return fn.countifs(*pairs)

    @staticmethod
    def index_match(
        return_table: str, return_column: str, lookup_value: str,
        lookup_table: str, lookup_column: str,
    ) -> str:
        return fn.index_match(
            ref.table_column(return_table, return_column),
            lookup_value,
            ref.table_column(lookup_table, lookup_column),
        )

    # -- plain-range fallbacks (no Table object required) ----------------
    @staticmethod
    def sum_range(sheet: str, cell_range: str) -> str:
        return fn.sum_(ref.sheet_range(sheet, cell_range))

    @staticmethod
    def average_range(sheet: str, cell_range: str, safe: bool = True) -> str:
        return fn.average(ref.sheet_range(sheet, cell_range), safe=safe)

    @staticmethod
    def count_range(sheet: str, cell_range: str) -> str:
        return fn.count(ref.sheet_range(sheet, cell_range))

    @staticmethod
    def counta_range(sheet: str, cell_range: str) -> str:
        return fn.counta(ref.sheet_range(sheet, cell_range))

    @staticmethod
    def max_range(sheet: str, cell_range: str, safe: bool = True) -> str:
        return fn.max_(ref.sheet_range(sheet, cell_range), safe=safe)

    @staticmethod
    def min_range(sheet: str, cell_range: str, safe: bool = True) -> str:
        return fn.min_(ref.sheet_range(sheet, cell_range), safe=safe)

    @staticmethod
    def sumifs_range(sheet: str, sum_range: str, *criteria: tuple[str, str]) -> str:
        """criteria: (criteria_range, literal_value) pairs, all on `sheet`."""
        pairs = tuple(
            (ref.sheet_range(sheet, crit_range), ref.quote_criteria(value))
            for crit_range, value in criteria
        )
        return fn.sumifs(ref.sheet_range(sheet, sum_range), *pairs)

    # -- derived metrics (take raw refs — table or range, your choice) ----
    @staticmethod
    def percentage_of_total(part_ref: str, total_ref: str, safe: bool = True) -> str:
        return fn.percentage_of_total(part_ref, total_ref, safe=safe)

    @staticmethod
    def growth(current_ref: str, previous_ref: str, safe: bool = True) -> str:
        return fn.growth(current_ref, previous_ref, safe=safe)

    @staticmethod
    def variance(actual_ref: str, budget_ref: str, safe: bool = True) -> str:
        return fn.variance(actual_ref, budget_ref, safe=safe)
