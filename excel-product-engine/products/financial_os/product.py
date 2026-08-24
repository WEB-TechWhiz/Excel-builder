"""Financial OS — the first product built on the engine.

    from products.financial_os.product import build_financial_os
    workbook = build_financial_os()
    workbook.save("output/financial_os.xlsx")

Build order matters: data sheets first (Dashboard's formulas reference
their tables by name), Dashboard next (needs the Goals sheet's
TypedTable for the progress summary), Reports and Settings last, then
the navigation menu goes on every sheet in one pass.
"""

from __future__ import annotations

from excel_engine.config.product_config import ProductConfig
from excel_engine.core.metadata import WorkbookMetadata
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.logging_config import get_logger
from excel_engine.navigation import apply_menu_to_all_sheets
from excel_engine.styles.style_manager import StyleManager
from products.financial_os.config import FINANCIAL_OS_CONFIG, MENU_ITEMS
from products.financial_os.sheets import (
    build_bills_sheet,
    build_dashboard_sheet,
    build_expenses_sheet,
    build_goals_sheet,
    build_income_sheet,
    build_investments_sheet,
    build_net_worth_sheet,
    build_reports_sheet,
    build_settings_sheet,
)

logger = get_logger("financial_os.product")


def build_financial_os(config: ProductConfig | None = None) -> ExcelWorkbook:
    config = config or FINANCIAL_OS_CONFIG
    style = StyleManager.for_theme(config.theme.name)

    workbook = ExcelWorkbook(
        metadata=WorkbookMetadata(title=config.name, author=config.author, version=config.version)
    )
    logger.info("Building %s v%s", config.name, config.version)

    build_income_sheet(workbook, style)
    build_expenses_sheet(workbook, style)
    build_bills_sheet(workbook, style)
    build_investments_sheet(workbook, style)
    build_net_worth_sheet(workbook, style)
    goals_table = build_goals_sheet(workbook, style)
    build_settings_sheet(workbook, style)

    build_dashboard_sheet(workbook, style, goals_table)
    build_reports_sheet(workbook, style)

    workbook.reorder_sheet("Dashboard", index=0)
    apply_menu_to_all_sheets(workbook, style, MENU_ITEMS, top_left="A1", item_width=3)

    logger.info("Build complete: %s", workbook.sheet_names)
    return workbook
