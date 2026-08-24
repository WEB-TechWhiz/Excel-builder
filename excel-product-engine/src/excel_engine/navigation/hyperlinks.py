"""Safe internal-hyperlink construction and validation.

Section 15 of the original spec: "avoid fragile navigation references"
and "validate all navigation links." Building the target string through
`internal_link` makes a broken link fail loudly at build time (the
target sheet genuinely doesn't exist yet); `validate_all_hyperlinks`
scans an already-built workbook for links that point nowhere, which
catches links built any other way too (e.g. Phase 4's `add_navbar` /
`add_button`, which build hyperlinks directly).
"""

from __future__ import annotations

from excel_engine.core.workbook import ExcelWorkbook
from excel_engine.exceptions.errors import WorkbookBuildError


def internal_link(workbook: ExcelWorkbook, target_sheet: str, target_cell: str = "A1") -> str:
    """Build a validated internal hyperlink target string
    (`#Sheet!A1` or `#'Sheet Name'!A1`), raising immediately if
    `target_sheet` doesn't exist in `workbook`.
    """
    if not workbook.has_sheet(target_sheet):
        raise WorkbookBuildError(
            f"Cannot link to sheet {target_sheet!r} — it doesn't exist. "
            f"Available sheets: {workbook.sheet_names}"
        )
    quoted = f"'{target_sheet}'" if " " in target_sheet else target_sheet
    return f"#{quoted}!{target_cell}"


def validate_all_hyperlinks(workbook: ExcelWorkbook) -> list[str]:
    """Scan every sheet's cells for internal hyperlinks (targets
    starting with '#') and return a list of problem descriptions — an
    empty list means every internal link points at a real sheet.

    Doesn't raise; callers (e.g. Phase 7's validators) decide how to
    react to a non-empty result.
    """
    problems: list[str] = []
    valid_sheets = set(workbook.sheet_names)

    for sheet_name in workbook.sheet_names:
        raw_ws = workbook.get_sheet(sheet_name).raw
        for row in raw_ws.iter_rows():
            for cell in row:
                link = cell.hyperlink
                if link is None or not link.target or not link.target.startswith("#"):
                    continue
                target_sheet = link.target[1:].split("!", 1)[0].strip("'")
                if target_sheet not in valid_sheets:
                    problems.append(
                        f"{sheet_name}!{cell.coordinate} links to missing sheet "
                        f"{target_sheet!r}"
                    )
    return problems
