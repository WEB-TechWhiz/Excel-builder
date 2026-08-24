"""Formula engine — safe reference construction plus a `Formula` builder
so no product/component code hand-concatenates Excel formula syntax.

    from excel_engine.formulas import Formula
    Formula.sum("Income", "Amount")   # -> "=SUM(Income[Amount])"
"""

from excel_engine.formulas.builder import Formula

__all__ = ["Formula"]
