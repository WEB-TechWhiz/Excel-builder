from excel_engine.formulas import Formula


def test_sum_uses_structured_reference():
    assert Formula.sum("Income", "Amount") == "=SUM(Income[Amount])"


def test_average_uses_structured_reference():
    assert Formula.average("Orders", "Amount") == "=IFERROR(AVERAGE(Orders[Amount]), 0)"


def test_count_counta_structured():
    assert Formula.count("Orders", "Date") == "=COUNT(Orders[Date])"
    assert Formula.counta("Orders", "Date") == "=COUNTA(Orders[Date])"


def test_max_min_structured():
    assert Formula.max("Orders", "Amount") == "=IFERROR(MAX(Orders[Amount]), 0)"
    assert Formula.min("Orders", "Amount") == "=IFERROR(MIN(Orders[Amount]), 0)"


def test_sumifs_quotes_and_structures_criteria():
    result = Formula.sumifs("Orders", "Amount", ("Colorway", "Saddle Amber"))
    assert result == '=SUMIFS(Orders[Amount], Orders[Colorway], "Saddle Amber")'


def test_sumifs_multiple_criteria():
    result = Formula.sumifs("Orders", "Amount", ("Colorway", "Amber"), ("Status", "Paid"))
    assert result == '=SUMIFS(Orders[Amount], Orders[Colorway], "Amber", Orders[Status], "Paid")'


def test_averageifs():
    result = Formula.averageifs("Orders", "Amount", ("Colorway", "Amber"))
    assert result == '=IFERROR(AVERAGEIFS(Orders[Amount], Orders[Colorway], "Amber"), 0)'


def test_countifs():
    result = Formula.countifs("Orders", ("Status", "Paid"))
    assert result == '=COUNTIFS(Orders[Status], "Paid")'


def test_index_match_uses_two_tables():
    result = Formula.index_match("Income", "Amount", '"Salary"', "Income", "Source")
    assert result == '=INDEX(Income[Amount], MATCH("Salary", Income[Source], 0))'


def test_sum_range_fallback():
    assert Formula.sum_range("Orders", "C2:C50") == "=SUM(Orders!C2:C50)"


def test_sum_range_quotes_spaced_sheet():
    assert Formula.sum_range("Order Data", "C2:C50") == "=SUM('Order Data'!C2:C50)"


def test_sumifs_range_fallback():
    result = Formula.sumifs_range("Orders", "C2:C50", ("B2:B50", "Amber"))
    assert result == '=SUMIFS(Orders!C2:C50, Orders!B2:B50, "Amber")'


def test_derived_metrics_take_raw_refs():
    assert Formula.percentage_of_total("B2", "B10") == "=IFERROR(B2/B10, 0)"
    assert Formula.growth("B2", "B1") == "=IFERROR((B2-B1)/B1, 0)"
    assert Formula.variance("B2", "C2") == "=IFERROR(B2-C2, 0)"
