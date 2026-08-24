"""Cell address parsing and manipulation (A1-style)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from excel_engine.exceptions.errors import CellAddressError

_ADDRESS_RE = re.compile(r"^\$?([A-Za-z]{1,3})\$?(\d+)$")


def column_letter_to_index(letters: str) -> int:
    """'A' -> 1, 'Z' -> 26, 'AA' -> 27 ..."""
    letters = letters.upper()
    result = 0
    for ch in letters:
        if not ("A" <= ch <= "Z"):
            raise CellAddressError(f"Invalid column letters: {letters!r}")
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result


def column_index_to_letter(index: int) -> str:
    """1 -> 'A', 26 -> 'Z', 27 -> 'AA' ..."""
    if index < 1:
        raise CellAddressError(f"Column index must be >= 1, got {index}")
    letters = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


@dataclass(frozen=True, slots=True)
class CellAddress:
    """An immutable (row, column) cell reference with A1-notation helpers."""

    row: int
    column: int

    def __post_init__(self) -> None:
        if self.row < 1:
            raise CellAddressError(f"Row must be >= 1, got {self.row}")
        if self.column < 1:
            raise CellAddressError(f"Column must be >= 1, got {self.column}")

    @classmethod
    def from_a1(cls, address: str) -> CellAddress:
        match = _ADDRESS_RE.match(address.strip())
        if not match:
            raise CellAddressError(f"Invalid A1 address: {address!r}")
        col_letters, row_digits = match.groups()
        return cls(row=int(row_digits), column=column_letter_to_index(col_letters))

    @property
    def column_letter(self) -> str:
        return column_index_to_letter(self.column)

    def to_a1(self, absolute: bool = False) -> str:
        prefix = "$" if absolute else ""
        return f"{prefix}{self.column_letter}{prefix}{self.row}"

    def offset(self, rows: int = 0, columns: int = 0) -> CellAddress:
        return CellAddress(row=self.row + rows, column=self.column + columns)

    def __str__(self) -> str:
        return self.to_a1()
