"""Workbook-wide navigation menu.

Phase 4's `components.add_navbar` draws one navbar wherever you call
it. This module is the difference between that and "the generated
workbook should feel like an application" (section 15): one call adds
a consistent navbar — with the right page marked active — to the top
of *every* page in the menu, and refuses to build anything if the menu
references a sheet that doesn't exist.
"""

from __future__ import annotations

from excel_engine.components.navbar import add_navbar
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import WorkbookBuildError
from excel_engine.styles.style_manager import StyleManager


def apply_menu_to_all_sheets(
    workbook: ExcelWorkbook,
    style: StyleManager,
    menu_items: list[str],
    top_left: str = "A1",
    item_width: int = 3,
) -> None:
    """Add `menu_items` as a navbar at `top_left` on every sheet named in
    `menu_items`, each showing its own tab as the active (bold,
    un-linked) item. Raises before writing anything if any menu item
    isn't a real sheet in `workbook`.
    """
    missing = [name for name in menu_items if not workbook.has_sheet(name)]
    if missing:
        raise WorkbookBuildError(
            f"Menu references sheet(s) that don't exist: {missing}. "
            f"Available: {workbook.sheet_names}"
        )

    for sheet_name in menu_items:
        ws = workbook.get_sheet(sheet_name)
        add_navbar(ws, style, menu_items, top_left=top_left, active=sheet_name,
                   item_width=item_width)
