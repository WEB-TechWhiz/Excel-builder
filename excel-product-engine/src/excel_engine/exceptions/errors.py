"""Custom exception hierarchy for the Excel Product Engine.

All engine and product code raises one of these instead of a bare
``Exception`` or a built-in exception, so callers can catch failures at
the right level of granularity instead of catching everything blindly.
"""

from __future__ import annotations


class ExcelEngineError(Exception):
    """Base class for every exception raised by the engine or a product."""


class WorkbookBuildError(ExcelEngineError):
    """Raised when a workbook cannot be assembled (sheet, table, chart, ...)."""


class ProductConfigurationError(ExcelEngineError):
    """Raised when product configuration is missing or invalid."""


class FormulaValidationError(ExcelEngineError):
    """Raised when a generated formula is malformed or references something invalid."""


class WorkbookValidationError(ExcelEngineError):
    """Raised when a built workbook fails structural or integrity validation."""


class ExportError(ExcelEngineError):
    """Raised when saving/exporting the final .xlsx (or a release package) fails."""


class CellAddressError(ExcelEngineError):
    """Raised when a cell or range address is malformed (e.g. bad A1 notation)."""


class SheetNotFoundError(ExcelEngineError):
    """Raised when code looks up a worksheet that doesn't exist in the workbook."""
