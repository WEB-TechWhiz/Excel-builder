from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.protection.cells import lock_range, unlock_range


def test_cells_locked_by_default():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Orders")
    assert ws.raw["A1"].protection.locked is True


def test_unlock_range_unlocks_every_cell_in_range():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Orders")
    unlock_range(ws, "A2:B3")
    for addr in ("A2", "B2", "A3", "B3"):
        assert ws.raw[addr].protection.locked is False
    assert ws.raw["C2"].protection.locked is True  # outside the range, untouched


def test_lock_range_relocks_a_previously_unlocked_range():
    wb = ExcelWorkbook()
    ws = wb.add_sheet("Orders")
    unlock_range(ws, "A1:A5")
    lock_range(ws, "A1:A5")
    assert ws.raw["A3"].protection.locked is True
