"""Data engine — typed tables, validation, named ranges, and demo-row
writing, all built on top of the Phase 1-4 core/components layers.

    from excel_engine.data.tables import add_typed_table, ColumnSchema
"""

from excel_engine.data.tables import ColumnSchema, TypedTable, add_typed_table

__all__ = ["ColumnSchema", "TypedTable", "add_typed_table"]
