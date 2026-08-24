from excel_engine.validation.report import ValidationIssue, ValidationReport, ValidationResult


def test_result_passes_with_no_issues():
    result = ValidationResult(category="Structure")
    assert result.passed is True


def test_result_fails_with_error_issue():
    result = ValidationResult(
        category="Structure",
        issues=(ValidationIssue(category="structure", message="missing sheet"),),
    )
    assert result.passed is False


def test_result_passes_with_only_warnings():
    result = ValidationResult(
        category="Structure",
        issues=(ValidationIssue(category="structure", message="fyi", severity="warning"),),
    )
    assert result.passed is True


def test_report_passes_only_if_every_result_passes():
    passing = ValidationResult(category="Structure")
    failing = ValidationResult(
        category="Formulas",
        issues=(ValidationIssue(category="formula", message="broken"),),
    )
    report = ValidationReport(product_name="Test", results=(passing, failing))
    assert report.passed is False
    assert len(report.all_issues) == 1


def test_report_format_matches_expected_style():
    report = ValidationReport(
        product_name="Financial OS",
        results=(ValidationResult(category="Structure"), ValidationResult(category="Formulas")),
    )
    text = report.format()
    assert "FINANCIAL OS VALIDATION" in text
    assert "Structure" in text
    assert "PASS" in text
    assert "STATUS: PASS" in text


def test_report_format_lists_issues_when_failing():
    report = ValidationReport(
        product_name="Financial OS",
        results=(ValidationResult(
            category="Structure",
            issues=(ValidationIssue(category="structure", message="Dashboard sheet missing"),),
        ),),
    )
    text = report.format()
    assert "STATUS: FAIL" in text
    assert "Dashboard sheet missing" in text
