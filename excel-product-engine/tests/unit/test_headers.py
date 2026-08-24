import pytest

from excel_engine.components.headers import add_section_header, add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.styles.style_manager import StyleManager


@pytest.fixture
def sheet():
    wb = ExcelWorkbook()
    return wb.add_sheet("Dashboard")


def test_title_banner_without_subtitle(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_title_banner(sheet, style, "Financial OS", width=5)
    assert sheet.get_value("A1") == "Financial OS"
    assert rng.to_a1() == "A1:E1"
    assert sheet.raw["A1"].fill.fgColor.rgb.endswith(style.palette.primary)


def test_title_banner_with_subtitle_spans_two_rows(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_title_banner(sheet, style, "Financial OS", subtitle="Auto-calculated", width=5)
    assert sheet.get_value("A2") == "Auto-calculated"
    assert rng.to_a1() == "A1:E2"
    assert sheet.raw["A2"].font.color.rgb.endswith(style.palette.on_primary)


def test_section_header(sheet):
    style = StyleManager.for_theme("premium")
    rng = add_section_header(sheet, style, "Chart Source Data", top_left="T5", width=2)
    assert sheet.get_value("T5") == "Chart Source Data"
    assert rng.to_a1() == "T5:U5"
