import pytest

from excel_engine.components.cards import add_kpi_card
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import CellAddressError
from excel_engine.styles.style_manager import StyleManager


@pytest.fixture
def sheet():
    wb = ExcelWorkbook()
    return wb.add_sheet("Dashboard")


def test_card_writes_label_and_formula(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_kpi_card(sheet, style, "Total Revenue", "=SUM(A1:A10)", top_left="B2")

    assert sheet.get_value("B2") == "TOTAL REVENUE"
    assert sheet.get_value("B3") == "=SUM(A1:A10)"
    assert rng.to_a1() == "B2:D4"


def test_card_applies_theme_styling(sheet):
    style = StyleManager.for_theme("premium")
    add_kpi_card(sheet, style, "Orders", "=COUNT(A1:A10)", top_left="B2")

    label_cell = sheet.raw["B2"]
    value_cell = sheet.raw["B3"]
    assert label_cell.font.color.rgb.endswith(style.palette.primary)
    assert value_cell.fill.fgColor.rgb.endswith(style.palette.surface)


def test_card_applies_number_format(sheet):
    style = StyleManager.for_theme("premium")
    add_kpi_card(sheet, style, "Revenue", "=1", top_left="B2", number_format='"₹"#,##0')
    assert sheet.raw["B3"].number_format == '"₹"#,##0'


def test_card_default_width_is_three_columns(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_kpi_card(sheet, style, "X", "=1", top_left="A1")
    assert rng.n_columns == 3


def test_card_rejects_bad_top_left(sheet):
    style = StyleManager.for_theme("premium")
    with pytest.raises(CellAddressError):
        add_kpi_card(sheet, style, "X", "=1", top_left="not-a-cell")
