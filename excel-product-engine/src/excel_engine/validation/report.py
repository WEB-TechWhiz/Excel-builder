"""Data model shared by every validator: one `ValidationIssue` per
problem found, rolled up into a `ValidationResult` per category, rolled
up into one `ValidationReport` for the whole workbook.

Not listed as its own file in the original spec's tree (section 3
lists workbook_validator.py / formula_validator.py /
structure_validator.py / integrity_validator.py only) — this is the
small shared data model those four files need, factored out once
rather than redefined in each.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["error", "warning"]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    category: str
    message: str
    severity: Severity = "error"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """One category's pass/fail plus whatever issues were found. Passes
    iff there are no `error`-severity issues (warnings don't fail it).
    """

    category: str
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The whole-workbook result — the programmatic equivalent of
    section 24's `validate.py` output. `format()` renders it the same
    way; Phase 9's CLI script is expected to just print that.
    """

    product_name: str
    results: tuple[ValidationResult, ...]

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def all_issues(self) -> list[ValidationIssue]:
        return [issue for result in self.results for issue in result.issues]

    def format(self) -> str:
        width = 40
        lines = ["=" * width, f"{self.product_name.upper()} VALIDATION", "=" * width, ""]
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"{result.category:<25} {status}")
        lines.append("")
        lines.append("=" * width)
        lines.append(f"STATUS: {'PASS' if self.passed else 'FAIL'}")
        lines.append("=" * width)
        if not self.passed:
            lines.append("")
            lines.append("Issues:")
            for issue in self.all_issues:
                if issue.severity == "error":
                    lines.append(f"  [{issue.category}] {issue.message}")
        return "\n".join(lines)
