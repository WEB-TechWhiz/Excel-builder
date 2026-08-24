#!/usr/bin/env python3
"""Validate an already-built workbook against its product's profile.

    python scripts/validate.py output/Financial_OS_v1.0.0.xlsx
    python scripts/validate.py output/Financial_OS_v1.0.0.xlsx --product financial_os
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from products.registry import PRODUCTS  # noqa: E402

from excel_engine.core.workbook import ExcelWorkbook  # noqa: E402
from excel_engine.validation import validate_workbook  # noqa: E402

DEFAULT_PRODUCT = "financial_os"


def validate(file_path: str, product_name: str = DEFAULT_PRODUCT) -> bool:
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {path}")
        raise SystemExit(1)

    if product_name not in PRODUCTS:
        print(f"Unknown product {product_name!r}. Available: {list(PRODUCTS)}")
        raise SystemExit(1)
    entry = PRODUCTS[product_name]

    workbook = ExcelWorkbook.load(path)
    report = validate_workbook(
        workbook,
        product_name=entry.config.name,
        required_sheets=entry.required_sheets,
        required_tables=entry.required_tables,
    )
    print(report.format())
    return report.passed


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate.py <file.xlsx> [--product <name>]")
        print(f"Available products: {list(PRODUCTS)}")
        raise SystemExit(1)

    file_path = sys.argv[1]
    product_name = DEFAULT_PRODUCT
    if "--product" in sys.argv:
        product_name = sys.argv[sys.argv.index("--product") + 1]

    passed = validate(file_path, product_name)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
