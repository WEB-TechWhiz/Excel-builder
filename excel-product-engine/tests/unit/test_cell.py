import pytest

from excel_engine.core.cell import CellAddress, column_index_to_letter, column_letter_to_index
from excel_engine.exceptions.errors import CellAddressError


def test_column_letter_roundtrip():
    assert column_letter_to_index("A") == 1
    assert column_letter_to_index("Z") == 26
    assert column_letter_to_index("AA") == 27
    assert column_index_to_letter(1) == "A"
    assert column_index_to_letter(27) == "AA"


def test_cell_address_from_a1():
    addr = CellAddress.from_a1("B5")
    assert addr.row == 5
    assert addr.column == 2
    assert addr.to_a1() == "B5"


def test_cell_address_offset():
    addr = CellAddress.from_a1("B5").offset(rows=2, columns=1)
    assert addr.to_a1() == "C7"


def test_invalid_address_raises():
    with pytest.raises(CellAddressError):
        CellAddress.from_a1("not-an-address")


def test_row_or_column_below_one_raises():
    with pytest.raises(CellAddressError):
        CellAddress(row=0, column=1)


def test_absolute_reference():
    addr = CellAddress.from_a1("C10")
    assert addr.to_a1(absolute=True) == "$C$10"
