from excel_engine.formulas.functions import (
    average,
    averageifs,
    count,
    counta,
    growth,
    if_,
    iferror,
    index_match,
    max_,
    min_,
    percentage_of_total,
    sum_,
    sumifs,
    variance,
)


def test_sum():
    assert sum_("Orders!C2:C50") == "=SUM(Orders!C2:C50)"


def test_count_counta():
    assert count("A2:A50") == "=COUNT(A2:A50)"
    assert counta("A2:A50") == "=COUNTA(A2:A50)"


def test_iferror_strips_leading_equals():
    assert iferror("=AVERAGE(A1:A5)") == "=IFERROR(AVERAGE(A1:A5), 0)"


def test_iferror_custom_fallback():
    assert iferror("SUM(A1:A5)", fallback='"n/a"') == '=IFERROR(SUM(A1:A5), "n/a")'


def test_average_safe_by_default():
    assert average("A1:A5") == "=IFERROR(AVERAGE(A1:A5), 0)"


def test_average_unsafe():
    assert average("A1:A5", safe=False) == "=AVERAGE(A1:A5)"


def test_max_min_safe_by_default():
    assert max_("A1:A5") == "=IFERROR(MAX(A1:A5), 0)"
    assert min_("A1:A5") == "=IFERROR(MIN(A1:A5), 0)"


def test_sumifs_single_criterion():
    result = sumifs("Orders!C2:C50", ("Orders!B2:B50", '"Amber"'))
    assert result == '=SUMIFS(Orders!C2:C50, Orders!B2:B50, "Amber")'


def test_sumifs_multiple_criteria():
    result = sumifs("C2:C50", ("B2:B50", '"Amber"'), ("D2:D50", '">100"'))
    assert result == '=SUMIFS(C2:C50, B2:B50, "Amber", D2:D50, ">100")'


def test_averageifs_safe():
    result = averageifs("C2:C50", ("B2:B50", '"Amber"'))
    assert result == '=IFERROR(AVERAGEIFS(C2:C50, B2:B50, "Amber"), 0)'


def test_if_builds_three_arg_if():
    assert if_("A1>0", '"Positive"', '"Non-positive"') == '=IF(A1>0, "Positive", "Non-positive")'


def test_index_match():
    result = index_match("Income[Amount]", '"Salary"', "Income[Source]")
    assert result == '=INDEX(Income[Amount], MATCH("Salary", Income[Source], 0))'


def test_percentage_of_total():
    assert percentage_of_total("B2", "B10") == "=IFERROR(B2/B10, 0)"


def test_growth():
    assert growth("B2", "B1") == "=IFERROR((B2-B1)/B1, 0)"


def test_variance():
    assert variance("B2", "C2") == "=IFERROR(B2-C2, 0)"
