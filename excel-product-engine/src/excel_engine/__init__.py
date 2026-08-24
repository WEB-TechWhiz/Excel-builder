"""Excel Product Engine — reusable core for generating Excel products.

Public API surface (grows as later phases land):

    from excel_engine import ExcelWorkbook, WorkbookMetadata
"""

from excel_engine.core.metadata import WorkbookMetadata
from excel_engine.core.workbook import ExcelWorkbook

__version__ = "0.1.0"

__all__ = ["ExcelWorkbook", "WorkbookMetadata", "__version__"]
