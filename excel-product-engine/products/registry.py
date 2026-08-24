"""Product registry — maps the product *name* used on the command line
(`python scripts/build.py financial_os`) to its builder function,
config, and validation profile.

Adding a second product means adding one entry here — `scripts/build.py`,
`validate.py`, and `release.py` never need to change.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from excel_engine.config.product_config import ProductConfig
from excel_engine.core.workbook import ExcelWorkbook
from products.financial_os.config import FINANCIAL_OS_CONFIG, REQUIRED_SHEETS, REQUIRED_TABLES
from products.financial_os.product import build_financial_os


@dataclass(frozen=True, slots=True)
class ProductRegistration:
    build: Callable[[], ExcelWorkbook]
    config: ProductConfig
    required_sheets: list[str]
    required_tables: dict[str, list[str]]


PRODUCTS: dict[str, ProductRegistration] = {
    "financial_os": ProductRegistration(
        build=build_financial_os,
        config=FINANCIAL_OS_CONFIG,
        required_sheets=REQUIRED_SHEETS,
        required_tables=REQUIRED_TABLES,
    ),
}
