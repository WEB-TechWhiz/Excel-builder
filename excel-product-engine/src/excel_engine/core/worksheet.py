"""Thin, typed wrapper around an openpyxl worksheet.

Product and component code should go through this class rather than
touching ``openpyxl.worksheet.worksheet.Worksheet`` directly, so the
engine can evolve its underlying library usage without breaking every
product built on top of it.
"""

from __future__ import annotations

from typing import Any

from openpyxl.worksheet.worksheet import Worksheet as _OpenpyxlWorksheet

from excel_engine.core.range import CellRange
from excel_engine.exceptions.errors import CellAddressError


class Worksheet:
    def __init__(self, raw: _OpenpyxlWorksheet) -> None:
        self._raw = raw

    # -- identity ---------------------------------------------------------
    @property
    def name(self) -> str:
        return str(self._raw.title)

    @property
    def raw(self) -> _OpenpyxlWorksheet:
        """Escape hatch to the underlying openpyxl worksheet.

        Prefer the typed methods below. Reach for this only when building
        a higher-level component (charts, tables, validation) that
        genuinely needs direct openpyxl access not yet wrapped here.
        """
        return self._raw

    # -- values / formulas --------------------------------------------------
    def set_value(self, address: str, value: Any) -> None:
        self._raw[address] = value

    def get_value(self, address: str) -> Any:
        return self._raw[address].value

    def set_formula(self, address: str, formula: str) -> None:
        if not formula.startswith("="):
            raise CellAddressError(f"Formula must start with '=': {formula!r}")
        self._raw[address] = formula

    # -- layout -----------------------------------------------------------
    def merge(self, cell_range: str | CellRange) -> None:
        ref = cell_range.to_a1() if isinstance(cell_range, CellRange) else cell_range
        self._raw.merge_cells(ref)

    def set_column_width(self, column: str, width: float) -> None:
        self._raw.column_dimensions[column].width = width

    def set_row_height(self, row: int, height: float) -> None:
        self._raw.row_dimensions[row].height = height

    def freeze_panes(self, address: str) -> None:
        self._raw.freeze_panes = address

    def hide(self) -> None:
        self._raw.sheet_state = "hidden"

    def set_tab_color(self, hex_color: str) -> None:
        self._raw.sheet_properties.tabColor = hex_color

    def show_gridlines(self, visible: bool) -> None:
        self._raw.sheet_view.showGridLines = visible

    def set_print_area(self, cell_range: str | CellRange) -> None:
        ref = cell_range.to_a1() if isinstance(cell_range, CellRange) else cell_range
        self._raw.print_area = ref

    def __repr__(self) -> str:
        return f"Worksheet(name={self.name!r})"
