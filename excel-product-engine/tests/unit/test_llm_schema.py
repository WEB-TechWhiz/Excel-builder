import pytest
from pydantic import ValidationError

from excel_engine.llm.schema import DashboardSpec, KPISpec, TableSheetSpec, WorkbookSpec


def _table(name="Orders", headers=("Date", "Customer", "Amount")):
    return TableSheetSpec(name=name, columns=[{"header": h} for h in headers])


def test_minimal_valid_spec():
    spec = WorkbookSpec(product_name="Sales Tracker", tables=[_table()])
    assert spec.theme == "premium"
    assert spec.dashboard.name == "Dashboard"


def test_unknown_theme_rejected():
    with pytest.raises(ValidationError):
        WorkbookSpec(product_name="X", theme="not-a-theme", tables=[_table()])


def test_duplicate_sheet_names_rejected():
    with pytest.raises(ValidationError):
        WorkbookSpec(
            product_name="X",
            tables=[_table(name="Dashboard")],  # collides with default dashboard.name
        )


def test_kpi_referencing_unknown_sheet_rejected():
    dashboard = DashboardSpec(kpis=[
        KPISpec(label="Revenue", source_sheet="DoesNotExist", source_column="Amount")
    ])
    with pytest.raises(ValidationError):
        WorkbookSpec(product_name="X", tables=[_table()], dashboard=dashboard)


def test_kpi_referencing_unknown_column_rejected():
    dashboard = DashboardSpec(kpis=[
        KPISpec(label="Revenue", source_sheet="Orders", source_column="NotAColumn")
    ])
    with pytest.raises(ValidationError):
        WorkbookSpec(product_name="X", tables=[_table()], dashboard=dashboard)


def test_valid_kpi_reference_accepted():
    dashboard = DashboardSpec(kpis=[
        KPISpec(label="Revenue", source_sheet="Orders", source_column="Amount", agg="SUM")
    ])
    spec = WorkbookSpec(product_name="X", tables=[_table()], dashboard=dashboard)
    assert spec.dashboard.kpis[0].agg == "SUM"


def test_invalid_agg_rejected():
    with pytest.raises(ValidationError):
        KPISpec(label="Revenue", source_sheet="Orders", source_column="Amount", agg="MEDIAN")


def test_requires_at_least_one_table():
    with pytest.raises(ValidationError):
        WorkbookSpec(product_name="X", tables=[])


def test_json_schema_is_generatable():
    """The schema must be usable as an Anthropic tool input_schema —
    generating it must never raise.
    """
    schema = WorkbookSpec.model_json_schema()
    assert schema["type"] == "object"
    assert "product_name" in schema["properties"]
