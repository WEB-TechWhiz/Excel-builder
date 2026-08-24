"""Builds a real ExcelWorkbook from a validated WorkbookSpec, using
Phase 1-4 engine primitives (ExcelWorkbook, StyleManager, components)
and the Phase 5 formula engine for KPI formulas.

This is the ONLY place LLM-derived data reaches openpyxl, and it only
ever does so through the same typed API a human developer would use —
no LLM output is ever eval'd, exec'd, or used to build formula text
outside of `Formula`'s fixed set of builders.
"""

from __future__ import annotations

from collections.abc import Callable

from excel_engine.components import add_data_table, add_kpi_card, add_title_banner
from excel_engine.core.cell import CellAddress
from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.formulas import Formula
from excel_engine.llm.schema import KPISpec, WorkbookSpec
from excel_engine.styles.style_manager import StyleManager

_NUMBER_FORMAT_TEMPLATES = {
    "currency": '"{sym}"#,##0',
    "number": "#,##0",
    "percent": "0.0%",
}

# Every aggregate KPISpec.agg allows, mapped straight onto the Phase 5
# formula engine's structured-reference builders (`=SUM(Orders[Amount])`
# etc.) — this module no longer builds any formula text itself.
_AGG_TO_FORMULA_METHOD: dict[str, Callable[[str, str], str]] = {
    "SUM": Formula.sum,
    "AVERAGE": Formula.average,
    "COUNT": Formula.count,
    "COUNTA": Formula.counta,
    "MAX": Formula.max,
    "MIN": Formula.min,
}


def _kpi_formula(kpi: KPISpec) -> str:
    return _AGG_TO_FORMULA_METHOD[kpi.agg](kpi.source_sheet, kpi.source_column)


def build_from_spec(spec: WorkbookSpec) -> ExcelWorkbook:
    """Pure builder: WorkbookSpec in, a ready-to-save ExcelWorkbook out.

    No network calls and no file I/O beyond the in-memory workbook, so
    this is fully testable without ever touching the LLM.
    """
    style = StyleManager.for_theme(spec.theme)
    workbook = ExcelWorkbook()

    for table_spec in spec.tables:
        sheet = workbook.add_sheet(table_spec.name)
        add_data_table(
            sheet, style, table_spec.column_headers,
            n_rows=table_spec.n_rows, table_name=table_spec.name,
        )

    dashboard = workbook.add_sheet(spec.dashboard.name)
    workbook.reorder_sheet(spec.dashboard.name, index=0)
    add_title_banner(
        dashboard, style, spec.product_name, subtitle=spec.dashboard.subtitle,
        top_left="A1", width=9,
    )

    number_formats = {
        key: (tmpl.format(sym=spec.currency_symbol) if "{sym}" in tmpl else tmpl)
        for key, tmpl in _NUMBER_FORMAT_TEMPLATES.items()
    }

    for i, kpi in enumerate(spec.dashboard.kpis):
        anchor = CellAddress(row=4 + (i // 3) * 4, column=1 + (i % 3) * 4)
        add_kpi_card(
            dashboard, style, kpi.label, _kpi_formula(kpi),
            top_left=anchor, number_format=number_formats[kpi.format],
        )

    return workbook
