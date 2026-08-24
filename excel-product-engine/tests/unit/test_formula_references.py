from excel_engine.formulas.references import (
    named_range,
    quote_criteria,
    sheet_range,
    table_column,
)


def test_table_column():
    assert table_column("Income", "Amount") == "Income[Amount]"


def test_sheet_range_simple_name():
    assert sheet_range("Orders", "C2:C50") == "Orders!C2:C50"


def test_sheet_range_quotes_spaced_name():
    assert sheet_range("Order Data", "C2:C50") == "'Order Data'!C2:C50"


def test_quote_criteria_wraps_in_quotes():
    assert quote_criteria("Saddle Amber") == '"Saddle Amber"'


def test_quote_criteria_escapes_embedded_quotes():
    assert quote_criteria('He said "hi"') == '"He said ""hi"""'


def test_named_range_is_passthrough():
    assert named_range("TotalRevenue") == "TotalRevenue"
