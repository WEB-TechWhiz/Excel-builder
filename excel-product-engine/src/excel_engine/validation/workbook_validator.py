"""The top-level validator: runs structure, formula, integrity, and
protection checks and combines them into one `ValidationReport` — the
programmatic equivalent of section 24's `validate.py` output. The
actual CLI script (`scripts/validate.py`, reading a file path from
argv and printing the report) is Phase 9's job; this is the engine
underneath it.
"""

from __future__ import annotations

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.validation.formula_validator import validate_formulas
from excel_engine.validation.integrity_validator import validate_integrity, validate_protection
from excel_engine.validation.report import ValidationReport
from excel_engine.validation.structure_validator import validate_structure


def validate_workbook(
    workbook: ExcelWorkbook,
    product_name: str,
    required_sheets: list[str] | None = None,
    required_tables: dict[str, list[str]] | None = None,
    required_named_ranges: list[str] | None = None,
    expected_formula_cells: list[tuple[str, str]] | None = None,
    expected_locked_formula_cells: list[tuple[str, str]] | None = None,
    expected_unlocked_input_ranges: list[tuple[str, str]] | None = None,
) -> ValidationReport:
    results = (
        validate_structure(workbook, required_sheets, required_tables, required_named_ranges),
        validate_formulas(workbook, expected_formula_cells),
        validate_integrity(workbook),
        validate_protection(workbook, expected_locked_formula_cells, expected_unlocked_input_ranges),
    )
    return ValidationReport(product_name=product_name, results=results)
