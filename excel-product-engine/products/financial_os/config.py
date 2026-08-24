"""Financial OS product configuration."""

from __future__ import annotations

from excel_engine.config.product_config import LocaleConfig, ProductConfig, ThemeConfig

FINANCIAL_OS_CONFIG = ProductConfig(
    name="Financial OS",
    version="1.0.0",
    author="MuffinCodes",
    locale=LocaleConfig(currency="INR", language="en", date_format="DD/MM/YYYY"),
    theme=ThemeConfig(name="premium"),
)

MENU_ITEMS = [
    "Dashboard", "Income", "Expenses", "Bills", "Investments",
    "Net Worth", "Goals", "Reports", "Settings",
]

# What scripts/validate.py (and the release pipeline) check a built
# Financial OS workbook against — see validation.workbook_validator.
REQUIRED_SHEETS = list(MENU_ITEMS)
REQUIRED_TABLES = {
    "Income": ["Income"],
    "Expenses": ["Expenses"],
    "Bills": ["Bills"],
    "Investments": ["Investments"],
    "Net Worth": ["NetWorth"],
    "Goals": ["Goals"],
}
