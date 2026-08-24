"""Integrity validation: no duplicate table names, no invalid
hyperlinks, no invalid ranges — plus protection checks (locked formula
cells, unlocked input cells).

The original spec's file tree (section 3) has no dedicated
`protection_validator.py`, so `validate_protection` lives here:
protection state being wrong (a formula cell left editable, an input
cell left locked) is itself a workbook-integrity problem, not a
separate concern.
"""

from __future__ import annotations

from excel_engine.core.range import CellRange
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import CellAddressError
from excel_engine.navigation.hyperlinks import validate_all_hyperlinks
from excel_engine.validation.report import ValidationIssue, ValidationResult


def validate_integrity(workbook: ExcelWorkbook) -> ValidationResult:
    issues: list[ValidationIssue] = []

    # No duplicate table names — Excel table names must be unique
    # workbook-wide, not just per-sheet.
    seen: dict[str, str] = {}
    for sheet_name in workbook.sheet_names:
        raw_ws = workbook.get_sheet(sheet_name).raw
        for table_name in raw_ws.tables:
            if table_name in seen:
                issues.append(ValidationIssue(
                    category="integrity",
                    message=f"Table name {table_name!r} is used on both "
                            f"{seen[table_name]!r} and {sheet_name!r} — table names "
                            f"must be unique workbook-wide",
                ))
            else:
                seen[table_name] = sheet_name

    # No invalid hyperlinks (reuses the Phase 6 navigation scanner, so
    # links built any way — navbar, button, or by hand — are covered).
    for problem in validate_all_hyperlinks(workbook):
        issues.append(ValidationIssue(category="integrity", message=problem))

    # No invalid table ranges.
    for sheet_name in workbook.sheet_names:
        raw_ws = workbook.get_sheet(sheet_name).raw
        for table_name, table_ref in raw_ws.tables.items():
            try:
                CellRange.from_a1(table_ref)
            except CellAddressError as exc:
                issues.append(ValidationIssue(
                    category="integrity",
                    message=f"Table {table_name!r} on {sheet_name!r} has an invalid "
                            f"range {table_ref!r}: {exc}",
                ))

    return ValidationResult(category="Integrity", issues=tuple(issues))


def validate_protection(
    workbook: ExcelWorkbook,
    expected_locked_formula_cells: list[tuple[str, str]] | None = None,
    expected_unlocked_input_ranges: list[tuple[str, str]] | None = None,
) -> ValidationResult:
    """There's no way to infer "this cell is supposed to be an input"
    purely from a built workbook — the caller declares what it expects,
    this checks the workbook actually matches.
    """
    issues: list[ValidationIssue] = []

    for sheet_name, cell_addr in expected_locked_formula_cells or []:
        if not workbook.has_sheet(sheet_name):
            continue
        ws = workbook.get_sheet(sheet_name)
        if not ws.raw[cell_addr].protection.locked:
            issues.append(ValidationIssue(
                category="protection",
                message=f"{sheet_name}!{cell_addr} should be locked (it holds a "
                        f"formula) but is unlocked",
            ))

    for sheet_name, range_addr in expected_unlocked_input_ranges or []:
        if not workbook.has_sheet(sheet_name):
            continue
        ws = workbook.get_sheet(sheet_name)
        rng = CellRange.from_a1(range_addr)
        for row in range(rng.start.row, rng.end.row + 1):
            for col in range(rng.start.column, rng.end.column + 1):
                cell = ws.raw.cell(row=row, column=col)
                if cell.protection.locked:
                    issues.append(ValidationIssue(
                        category="protection",
                        message=f"{sheet_name}!{cell.coordinate} should be an "
                                f"unlocked input cell but is locked",
                    ))

    return ValidationResult(category="Protection", issues=tuple(issues))
