"""Tests for the Phase 9 CLI scripts (scripts/build.py, validate.py,
release.py). Uses a mix of direct function calls (for logic that's
awkward to force via subprocess, like a validation failure or the
overwrite guard) and real subprocess invocations (to prove the actual
CLI entry points work end-to-end, exit codes included).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from products.registry import PRODUCTS, ProductRegistration
from scripts.build import build
from scripts.release import release
from scripts.validate import validate

REPO_ROOT = Path(__file__).resolve().parents[2]


# -- direct function-level tests -------------------------------------------

def test_build_writes_versioned_filename(tmp_path):
    out_path = build("financial_os", output_dir=tmp_path)
    assert out_path.name == "Financial_OS_v1.0.0.xlsx"
    assert out_path.exists()


def test_build_unknown_product_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        build("not_a_real_product")
    assert exc_info.value.code == 1


def test_build_refuses_to_export_when_validation_fails(tmp_path, monkeypatch):
    """A product whose builder produces an incomplete workbook must not
    export anything — section 23: "Do not report success if validation
    fails."
    """
    from excel_engine.core.workbook import ExcelWorkbook

    def broken_builder():
        wb = ExcelWorkbook()
        wb.add_sheet("Dashboard")  # missing every other required sheet
        return wb

    broken_entry = ProductRegistration(
        build=broken_builder,
        config=PRODUCTS["financial_os"].config,
        required_sheets=PRODUCTS["financial_os"].required_sheets,
        required_tables=PRODUCTS["financial_os"].required_tables,
    )
    monkeypatch.setitem(PRODUCTS, "broken_product", broken_entry)

    with pytest.raises(SystemExit) as exc_info:
        build("broken_product", output_dir=tmp_path)
    assert exc_info.value.code == 1
    assert list(tmp_path.iterdir()) == []  # nothing was exported


def test_validate_passes_for_a_real_build(tmp_path):
    out_path = build("financial_os", output_dir=tmp_path)
    assert validate(str(out_path)) is True


def test_validate_fails_for_an_incomplete_workbook(tmp_path):
    from excel_engine.core.workbook import ExcelWorkbook

    wb = ExcelWorkbook()
    wb.add_sheet("Dashboard")
    path = tmp_path / "incomplete.xlsx"
    wb.save(path)

    assert validate(str(path)) is False


def test_validate_missing_file_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        validate("/tmp/definitely-does-not-exist-12345.xlsx")
    assert exc_info.value.code == 1


def test_release_creates_expected_directory_structure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("scripts.release._REPO_ROOT", tmp_path)

    xlsx_path = release("financial_os")

    release_dir = tmp_path / "dist" / "financial-os"
    assert xlsx_path == release_dir / "Financial_OS_v1.0.0.xlsx"
    assert xlsx_path.exists()
    assert (release_dir / "Documentation" / "README.md").exists()
    assert (release_dir / "License" / "LICENSE.txt").exists()
    assert (release_dir / "Release" / "RELEASE_NOTES.txt").exists()


def test_release_refuses_to_overwrite_without_force(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("scripts.release._REPO_ROOT", tmp_path)

    release("financial_os")
    with pytest.raises(SystemExit) as exc_info:
        release("financial_os")  # no --force
    assert exc_info.value.code == 1


def test_release_force_does_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("scripts.release._REPO_ROOT", tmp_path)

    first = release("financial_os")
    first_mtime = first.stat().st_mtime_ns
    second = release("financial_os", force=True)
    assert second.stat().st_mtime_ns >= first_mtime


# -- real subprocess tests: prove the actual CLI entry points work ----------

def test_build_cli_end_to_end(tmp_path):
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build.py"), "financial_os"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "BUILD SUCCESSFUL" in result.stdout
    assert (tmp_path / "output" / "Financial_OS_v1.0.0.xlsx").exists()


def test_validate_cli_end_to_end(tmp_path):
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build.py"), "financial_os"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate.py"),
         "output/Financial_OS_v1.0.0.xlsx"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "STATUS: PASS" in result.stdout


def test_full_recalculated_build_has_zero_formula_errors(tmp_path):
    """End-to-end proof the CLI's output isn't just structurally valid —
    the formulas it contains actually compute (LibreOffice recalc).
    """
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build.py"), "financial_os"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    out_path = tmp_path / "output" / "Financial_OS_v1.0.0.xlsx"
    recalc_script = str(REPO_ROOT / "scripts" / "recalc.py")
    result = subprocess.run(
        [sys.executable, recalc_script, str(out_path), "150"],
        capture_output=True, text=True, timeout=120,
    )
    report = json.loads(result.stdout)
    assert report["status"] == "success", report
    assert report["total_errors"] == 0
