"""Natural-language front-end: turn a plain-English prompt into a
validated WorkbookSpec (via the Claude API's tool use), then build a
real workbook from it using the Phase 1-4 engine — no LLM output ever
touches openpyxl directly, it only ever produces the constrained
WorkbookSpec that `llm.builder` consumes.

Optional — requires `pip install -e ".[llm]"` and ANTHROPIC_API_KEY.
The rest of the engine has no dependency on this package.

    from excel_engine.llm import generate_workbook
    generate_workbook("Make me a sales tracker with total revenue")
"""

from excel_engine.llm.generate import generate_workbook
from excel_engine.llm.schema import WorkbookSpec

__all__ = ["generate_workbook", "WorkbookSpec"]
