"""Proves the full offline pipeline (WorkbookSpec -> ExcelWorkbook -> real
.xlsx) doesn't just produce well-formed *text* formulas — they actually
calculate correctly when opened in a real spreadsheet engine.

Does not touch the network/LLM: it hand-builds a WorkbookSpec, exactly
as `llm.client.get_workbook_spec` would after a successful Claude call,
and feeds it straight to the builder.
"""

import json
import subprocess
import sys

from pathlib import Path

from excel_engine.llm.builder import build_from_spec
from excel_engine.llm.schema import DashboardSpec, KPISpec, TableSheetSpec, WorkbookSpec

RECALC_SCRIPT = str(Path(__file__).resolve().parents[2] / "scripts" / "recalc.py")


def test_llm_generated_workbook_recalculates_without_errors(tmp_path):
    spec = WorkbookSpec(
        product_name="Sales Tracker",
        theme="premium",
        currency_symbol="₹",
        tables=[
            TableSheetSpec(
                name="Orders",
                columns=[{"header": "Date"}, {"header": "Customer"}, {"header": "Amount"}],
                n_rows=20,
            )
        ],
        dashboard=DashboardSpec(kpis=[
            KPISpec(label="Total Revenue", source_sheet="Orders",
                    source_column="Amount", agg="SUM", format="currency"),
            KPISpec(label="Avg Order", source_sheet="Orders",
                    source_column="Amount", agg="AVERAGE", format="currency"),
            KPISpec(label="Total Orders", source_sheet="Orders",
                    source_column="Date", agg="COUNTA", format="number"),
        ]),
    )

    workbook = build_from_spec(spec)
    orders = workbook.get_sheet("Orders")
    orders.set_value("A2", "2026-07-01")
    orders.set_value("B2", "Ananya Verma")
    orders.set_value("C2", 2499)
    orders.set_value("A3", "2026-07-04")
    orders.set_value("B3", "Rohan Gupta")
    orders.set_value("C3", 1899)

    out_path = workbook.save(tmp_path / "sales_tracker.xlsx")

    result = subprocess.run(
        [sys.executable, RECALC_SCRIPT, str(out_path), "20"],
        capture_output=True, text=True, timeout=60,
    )
    report = json.loads(result.stdout)

    assert report["status"] == "success"
    assert report["total_errors"] == 0
    assert report["total_formulas"] == 3
