"""Data validation helpers — dropdowns, numeric/date ranges, and
required-input rules, applied through the core `Worksheet` wrapper.
"""

from __future__ import annotations

from datetime import date

from openpyxl.worksheet.datavalidation import DataValidation

from excel_engine.core.range import CellRange
from excel_engine.core.worksheet import Worksheet


def _ref(cell_range: str | CellRange) -> str:
    return cell_range.to_a1() if isinstance(cell_range, CellRange) else cell_range


def add_dropdown(
    ws: Worksheet, cell_range: str | CellRange, options: list[str], allow_blank: bool = True
) -> None:
    """A dropdown list restricted to `options`; typing anything else is
    rejected with a visible Excel error.
    """
    dv = DataValidation(
        type="list", formula1='"{}"'.format(",".join(options)), allow_blank=allow_blank
    )
    dv.error = "Please choose a value from the dropdown."
    dv.errorTitle = "Invalid entry"
    ws.raw.add_data_validation(dv)
    dv.add(_ref(cell_range))


def add_number_range(
    ws: Worksheet,
    cell_range: str | CellRange,
    minimum: float,
    maximum: float,
    allow_blank: bool = True,
) -> None:
    dv = DataValidation(
        type="decimal", operator="between",
        formula1=str(minimum), formula2=str(maximum), allow_blank=allow_blank,
    )
    dv.error = f"Enter a number between {minimum} and {maximum}."
    dv.errorTitle = "Out of range"
    ws.raw.add_data_validation(dv)
    dv.add(_ref(cell_range))


def add_date_range(
    ws: Worksheet,
    cell_range: str | CellRange,
    earliest: date,
    latest: date,
    allow_blank: bool = True,
) -> None:
    dv = DataValidation(
        type="date", operator="between",
        formula1=earliest.isoformat(), formula2=latest.isoformat(), allow_blank=allow_blank,
    )
    dv.error = f"Enter a date between {earliest} and {latest}."
    dv.errorTitle = "Out of range"
    ws.raw.add_data_validation(dv)
    dv.add(_ref(cell_range))


def add_required(ws: Worksheet, cell_range: str | CellRange) -> None:
    """Rejects a blank cell, regardless of the value's type — uses a
    custom formula (`<>""`) rather than a type-specific rule, so it
    works uniformly for text, number, or date cells.
    """
    range_obj = cell_range if isinstance(cell_range, CellRange) else CellRange.from_a1(cell_range)
    top_left = range_obj.start.to_a1()
    dv = DataValidation(type="custom", formula1=f'{top_left}<>""', allow_blank=False)
    dv.error = "This field is required."
    dv.errorTitle = "Missing value"
    ws.raw.add_data_validation(dv)
    dv.add(range_obj.to_a1())
