"""Navigation engine — a workbook-wide menu (consistent navbar + active-
page state on every page) plus link validation, on top of Phase 4's
navbar/button components.

    from excel_engine.navigation import apply_menu_to_all_sheets
"""

from excel_engine.navigation.hyperlinks import internal_link, validate_all_hyperlinks
from excel_engine.navigation.menu import apply_menu_to_all_sheets

__all__ = ["apply_menu_to_all_sheets", "internal_link", "validate_all_hyperlinks"]
