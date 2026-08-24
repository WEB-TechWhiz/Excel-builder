"""Structure validation: required sheets exist, required tables exist
on the right sheets, required named ranges exist.
"""

from __future__ import annotations

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.validation.report import ValidationIssue, ValidationResult


def validate_structure(
    workbook: ExcelWorkbook,
    required_sheets: list[str] | None = None,
    required_tables: dict[str, list[str]] | None = None,
    required_named_ranges: list[str] | None = None,
) -> ValidationResult:
    """`required_tables` maps a sheet name to the table name(s) expected
    on it, e.g. `{"Orders": ["Orders"]}`.
    """
    issues: list[ValidationIssue] = []

    for sheet_name in required_sheets or []:
        if not workbook.has_sheet(sheet_name):
            issues.append(ValidationIssue(
                category="structure",
                message=f"Required sheet {sheet_name!r} is missing. "
                        f"Available: {workbook.sheet_names}",
            ))

    for sheet_name, table_names in (required_tables or {}).items():
        if not workbook.has_sheet(sheet_name):
            continue  # already reported above
        raw_ws = workbook.get_sheet(sheet_name).raw
        existing = set(raw_ws.tables.keys())
        for table_name in table_names:
            if table_name not in existing:
                issues.append(ValidationIssue(
                    category="structure",
                    message=f"Sheet {sheet_name!r} is missing required table "
                            f"{table_name!r}. Found: {sorted(existing)}",
                ))

    defined_names = set(workbook.raw.defined_names.keys())
    for name in required_named_ranges or []:
        if name not in defined_names:
            issues.append(ValidationIssue(
                category="structure",
                message=f"Required named range {name!r} is missing. "
                        f"Found: {sorted(defined_names)}",
            ))

    return ValidationResult(category="Structure", issues=tuple(issues))
