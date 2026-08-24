import pytest

from excel_engine.core.range import CellRange
from excel_engine.exceptions.errors import CellAddressError


def test_range_from_a1():
    rng = CellRange.from_a1("B2:D10")
    assert rng.n_rows == 9
    assert rng.n_columns == 3
    assert rng.to_a1() == "B2:D10"


def test_single_cell_range_collapses():
    rng = CellRange.from_a1("A1")
    assert rng.to_a1() == "A1"
    assert rng.n_rows == 1
    assert rng.n_columns == 1


def test_range_with_sheet_name():
    rng = CellRange.from_a1("A1:A5")
    assert rng.to_a1(sheet="Orders") == "Orders!A1:A5"


def test_range_with_spaced_sheet_name_is_quoted():
    rng = CellRange.from_a1("A1:A5")
    assert rng.to_a1(sheet="Order Data") == "'Order Data'!A1:A5"


def test_invalid_range_raises():
    with pytest.raises(CellAddressError):
        CellRange.from_a1("D10:B2")
