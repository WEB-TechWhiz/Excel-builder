"""Settings sheet: a few labeled-input preferences (Phase 4's
`components.add_labeled_input`), not a data table.
"""

from __future__ import annotations

from excel_engine.components import add_labeled_input, add_title_banner
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.protection import apply_standard_protection
from excel_engine.styles.style_manager import StyleManager


def build_settings_sheet(workbook: ExcelWorkbook, style: StyleManager) -> None:
    ws = workbook.add_sheet("Settings")
    add_title_banner(ws, style, "Settings", subtitle="Blue text = your data",
                      top_left="A2", width=5)

    add_labeled_input(ws, style, "Currency", top_left="A5", default_value="INR")
    add_labeled_input(ws, style, "Monthly Income Goal", top_left="A6", default_value=100000)
    add_labeled_input(ws, style, "Emergency Fund Target", top_left="A7", default_value=300000)

    apply_standard_protection(ws, editable_ranges=["C5:D7"])
