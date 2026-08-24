#!/usr/bin/env python3
"""Build a product end-to-end: config -> workbook -> validate -> export.

    python scripts/build.py financial_os

Reports 4 real, individually-observable steps — not the original
spec's illustrative 8 (Load/Workbook/Data model/Formulas/Components/
Charts/Validate/Package), since this engine's sheet builders create
tables, formulas, components, and charts together per-sheet rather than
as separate global passes over the whole workbook. See docs/
architecture.md's Phase 9 notes for why 4 honest steps beat 8 that
would only be theater.

Per section 23 of the original spec: never reports success if
validation fails — the file is not written in that case.
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from products.registry import PRODUCTS  # noqa: E402

from excel_engine.exceptions.errors import ExcelEngineError  # noqa: E402
from excel_engine.validation import validate_workbook  # noqa: E402

BANNER = "MUFFINCODES EXCEL PRODUCT ENGINE"
WIDTH = 40


def _step_line(n: int, total: int, label: str, ok: bool = True) -> None:
    mark = "\u2713" if ok else "\u2717"
    try:
        print(f"[{n}/{total}] {label:<28}{mark}")
    except UnicodeEncodeError:
        ascii_mark = "[OK]" if ok else "[FAIL]"
        print(f"[{n}/{total}] {label:<28}{ascii_mark}")


def build(product_name: str, output_dir: str | Path = "output") -> Path:
    if product_name not in PRODUCTS:
        print(f"Unknown product {product_name!r}. Available: {list(PRODUCTS)}")
        raise SystemExit(1)

    entry = PRODUCTS[product_name]
    total_steps = 4

    print("=" * WIDTH)
    print(BANNER)
    print("=" * WIDTH)
    print()
    print(f"Product: {entry.config.name}")
    print(f"Version: {entry.config.version}")
    print()

    config = entry.config  # already loaded via the registry import
    _step_line(1, total_steps, "Loading configuration")

    try:
        workbook = entry.build()
    except ExcelEngineError as exc:
        _step_line(2, total_steps, "Building workbook", ok=False)
        print()
        print(f"BUILD FAILED — {exc}")
        raise SystemExit(1) from exc
    _step_line(2, total_steps, "Building workbook")

    report = validate_workbook(
        workbook,
        product_name=config.name,
        required_sheets=entry.required_sheets,
        required_tables=entry.required_tables,
    )
    if not report.passed:
        _step_line(3, total_steps, "Running validation", ok=False)
        print()
        print(report.format())
        print()
        print("BUILD FAILED — see validation issues above. Nothing was exported.")
        raise SystemExit(1)
    _step_line(3, total_steps, "Running validation")

    filename = f"{config.name.replace(' ', '_')}_v{config.version}.xlsx"
    output_path = workbook.save(Path(output_dir) / filename)
    _step_line(4, total_steps, "Exporting XLSX")

    print()
    print("BUILD SUCCESSFUL")
    print()
    print("Output:")
    print(f"  {output_path}")
    return output_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/build.py <product_name>")
        print(f"Available products: {list(PRODUCTS)}")
        raise SystemExit(1)
    build(sys.argv[1])


if __name__ == "__main__":
    main()
