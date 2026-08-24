"""One string-builder per supported Excel function. These are
deliberately dumb — they just assemble `=FUNC(args)` correctly. Picking
*which* reference style (table vs. plain range) to pass in is the
caller's job, usually via `excel_engine.formulas.builder.Formula`.

XLOOKUP is intentionally not implemented here: it was tested against
this project's LibreOffice-based recalc harness and returned `#NAME?`
(see docs/architecture.md). `index_match` is the supported lookup —
it works everywhere XLOOKUP does and everywhere it doesn't.
"""

from __future__ import annotations


def sum_(ref: str) -> str:
    return f"=SUM({ref})"


def count(ref: str) -> str:
    return f"=COUNT({ref})"


def counta(ref: str) -> str:
    return f"=COUNTA({ref})"


def iferror(expr: str, fallback: str = "0") -> str:
    """Wrap a formula (with or without a leading '=') in IFERROR."""
    inner = expr[1:] if expr.startswith("=") else expr
    return f"=IFERROR({inner}, {fallback})"


def average(ref: str, safe: bool = True) -> str:
    expr = f"=AVERAGE({ref})"
    return iferror(expr) if safe else expr


def max_(ref: str, safe: bool = True) -> str:
    expr = f"=MAX({ref})"
    return iferror(expr) if safe else expr


def min_(ref: str, safe: bool = True) -> str:
    expr = f"=MIN({ref})"
    return iferror(expr) if safe else expr


def _criteria_clause(criteria_pairs: tuple[tuple[str, str], ...]) -> str:
    return ", ".join(f"{crit_ref}, {crit_val}" for crit_ref, crit_val in criteria_pairs)


def sumifs(sum_ref: str, *criteria_pairs: tuple[str, str]) -> str:
    """`sumifs(rev_ref, (cat_ref, '"Amber"'))` -> `=SUMIFS(rev_ref, cat_ref, "Amber")`.
    Criteria values must already be formula-ready literals — build
    string criteria with `references.quote_criteria`.
    """
    return f"=SUMIFS({sum_ref}, {_criteria_clause(criteria_pairs)})"


def averageifs(avg_ref: str, *criteria_pairs: tuple[str, str], safe: bool = True) -> str:
    expr = f"=AVERAGEIFS({avg_ref}, {_criteria_clause(criteria_pairs)})"
    return iferror(expr) if safe else expr


def countifs(*criteria_pairs: tuple[str, str]) -> str:
    return f"=COUNTIFS({_criteria_clause(criteria_pairs)})"


def if_(condition: str, if_true: str, if_false: str) -> str:
    return f"=IF({condition}, {if_true}, {if_false})"


def index_match(return_ref: str, lookup_value: str, lookup_ref: str) -> str:
    """The compatibility-safe lookup. `lookup_value` should already be a
    formula-ready literal or cell reference (use
    `references.quote_criteria` for a raw string).
    """
    return f"=INDEX({return_ref}, MATCH({lookup_value}, {lookup_ref}, 0))"


def percentage_of_total(part_ref: str, total_ref: str, safe: bool = True) -> str:
    expr = f"={part_ref}/{total_ref}"
    return iferror(expr) if safe else expr


def growth(current_ref: str, previous_ref: str, safe: bool = True) -> str:
    """Period-over-period growth: (current - previous) / previous."""
    expr = f"=({current_ref}-{previous_ref})/{previous_ref}"
    return iferror(expr) if safe else expr


def variance(actual_ref: str, budget_ref: str, safe: bool = True) -> str:
    """Actual vs. budget variance: actual - budget."""
    expr = f"={actual_ref}-{budget_ref}"
    return iferror(expr) if safe else expr
