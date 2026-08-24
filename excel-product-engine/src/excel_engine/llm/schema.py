"""The structured contract between an LLM and the deterministic engine.

An LLM is only ever allowed to produce a ``WorkbookSpec`` — never raw
code, never direct cell writes. Every field maps onto something
Phase 1-4 already knows how to build (a dashboard with KPI cards + data
tables); nothing here promises features the engine doesn't have yet
(charts, dropdowns, formulas beyond simple aggregates — those wait for
their own phases).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from excel_engine.config.themes import AVAILABLE_THEMES

AggFunc = Literal["SUM", "AVERAGE", "COUNT", "COUNTA", "MAX", "MIN"]
NumberFormat = Literal["currency", "number", "percent"]


class TableColumnSpec(BaseModel):
    header: str


class TableSheetSpec(BaseModel):
    name: str
    columns: list[TableColumnSpec] = Field(min_length=1, max_length=15)
    n_rows: int = Field(default=50, ge=1, le=1000)

    @property
    def column_headers(self) -> list[str]:
        return [c.header for c in self.columns]


class KPISpec(BaseModel):
    label: str
    source_sheet: str
    source_column: str
    agg: AggFunc = "SUM"
    format: NumberFormat = "number"


class DashboardSpec(BaseModel):
    name: str = "Dashboard"
    subtitle: str = "Auto-calculated"
    kpis: list[KPISpec] = Field(default_factory=list, max_length=8)


class WorkbookSpec(BaseModel):
    """The full, validated plan for one generated workbook."""

    product_name: str
    theme: str = "premium"
    currency_symbol: str = "₹"
    tables: list[TableSheetSpec] = Field(min_length=1, max_length=10)
    dashboard: DashboardSpec = Field(default_factory=DashboardSpec)

    @model_validator(mode="after")
    def _validate_theme(self) -> WorkbookSpec:
        if self.theme not in AVAILABLE_THEMES:
            raise ValueError(f"Unknown theme {self.theme!r}. Available: {AVAILABLE_THEMES}")
        return self

    @model_validator(mode="after")
    def _validate_unique_sheet_names(self) -> WorkbookSpec:
        names = [t.name for t in self.tables] + [self.dashboard.name]
        if len(names) != len(set(names)):
            raise ValueError(f"Sheet names must be unique, got: {names}")
        return self

    @model_validator(mode="after")
    def _validate_kpi_references(self) -> WorkbookSpec:
        tables_by_name = {t.name: t for t in self.tables}
        for kpi in self.dashboard.kpis:
            table = tables_by_name.get(kpi.source_sheet)
            if table is None:
                raise ValueError(
                    f"KPI {kpi.label!r} references sheet {kpi.source_sheet!r}, "
                    f"which isn't one of the tables: {list(tables_by_name)}"
                )
            if kpi.source_column not in table.column_headers:
                raise ValueError(
                    f"KPI {kpi.label!r} references column {kpi.source_column!r} "
                    f"on sheet {kpi.source_sheet!r}, but its columns are: "
                    f"{table.column_headers}"
                )
        return self
