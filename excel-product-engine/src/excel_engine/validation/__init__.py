"""Validation engine — structure, formula, integrity, and protection
checks, combined into one report.

    from excel_engine.validation import validate_workbook
    report = validate_workbook(workbook, "Financial OS", required_sheets=["Dashboard"])
    print(report.format())
    assert report.passed
"""

from excel_engine.validation.report import ValidationIssue, ValidationReport, ValidationResult
from excel_engine.validation.workbook_validator import validate_workbook

__all__ = ["validate_workbook", "ValidationReport", "ValidationResult", "ValidationIssue"]
