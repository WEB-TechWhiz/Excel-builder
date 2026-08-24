"""Rectangular cell ranges built from two CellAddress corners."""

from __future__ import annotations

from dataclasses import dataclass

from excel_engine.core.cell import CellAddress
from excel_engine.exceptions.errors import CellAddressError


@dataclass(frozen=True, slots=True)
class CellRange:
    start: CellAddress
    end: CellAddress

    def __post_init__(self) -> None:
        if self.end.row < self.start.row or self.end.column < self.start.column:
            raise CellAddressError(
                f"Range end {self.end} must be on or after range start {self.start}"
            )

    @classmethod
    def from_a1(cls, address: str) -> CellRange:
        if ":" not in address:
            single = CellAddress.from_a1(address)
            return cls(start=single, end=single)
        start_str, end_str = address.split(":", 1)
        return cls(start=CellAddress.from_a1(start_str), end=CellAddress.from_a1(end_str))

    def to_a1(self, sheet: str | None = None, absolute: bool = False) -> str:
        if self.start == self.end:
            base = self.start.to_a1(absolute)
        else:
            base = f"{self.start.to_a1(absolute)}:{self.end.to_a1(absolute)}"
        if sheet:
            quoted = f"'{sheet}'" if " " in sheet else sheet
            return f"{quoted}!{base}"
        return base

    @property
    def n_rows(self) -> int:
        return self.end.row - self.start.row + 1

    @property
    def n_columns(self) -> int:
        return self.end.column - self.start.column + 1

    def __str__(self) -> str:
        return self.to_a1()
