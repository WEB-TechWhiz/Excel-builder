"""UI components — reusable, theme-driven building blocks (cards,
headers, tables, inputs, navbar, buttons, progress bars, footers) that
products compose into sheets.

Every component takes a `Worksheet` + a `StyleManager` and returns the
`CellRange` it occupies, so callers can stack components without
recomputing positions by hand.

    from excel_engine.components import add_kpi_card, add_title_banner
"""

from excel_engine.components.buttons import add_button
from excel_engine.components.cards import add_kpi_card
from excel_engine.components.footers import add_footer
from excel_engine.components.headers import add_section_header, add_title_banner
from excel_engine.components.inputs import add_labeled_input
from excel_engine.components.navbar import add_navbar
from excel_engine.components.progress import add_progress_bar
from excel_engine.components.tables import add_data_table

__all__ = [
    "add_button",
    "add_kpi_card",
    "add_footer",
    "add_section_header",
    "add_title_banner",
    "add_labeled_input",
    "add_navbar",
    "add_progress_bar",
    "add_data_table",
]
