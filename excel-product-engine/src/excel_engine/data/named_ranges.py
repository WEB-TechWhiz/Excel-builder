"""Centralized named-range (defined name) creation.

Use named ranges when they genuinely improve formula/navigation
readability — not for every range in a workbook (see section 14 of the
original spec: avoid unnecessary named ranges).
"""

from __future__ import annotations

from openpyxl.workbook.defined_name import DefinedName

from excel_engine.core.range import CellRange
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import WorkbookBuildError


def add_named_range(
    workbook: ExcelWorkbook, name: str, sheet: str, cell_range: str | CellRange
) -> None:
    """Register `name` as a defined name pointing at `cell_range` on
    `sheet`. `name` must be a valid Excel defined-name identifier
    (letters/digits/underscore, not starting with a digit).
    """
    if not name.isidentifier():
        raise WorkbookBuildError(
            f"{name!r} is not a valid Excel defined name "
            "(letters, digits, underscore only; can't start with a digit)"
        )
    range_obj = cell_range if isinstance(cell_range, CellRange) else CellRange.from_a1(cell_range)
    formula = range_obj.to_a1(sheet=sheet, absolute=True)
    workbook.raw.defined_names[name] = DefinedName(name, attr_text=formula)


def list_named_ranges(workbook: ExcelWorkbook) -> list[str]:
    return list(workbook.raw.defined_names.keys())


def get_named_range_formula(workbook: ExcelWorkbook, name: str) -> str:
    try:
        defined_name = workbook.raw.defined_names[name]
    except KeyError as exc:
        raise WorkbookBuildError(f"No named range called {name!r}") from exc
    return str(defined_name.attr_text)
