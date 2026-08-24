"""Write demo/example rows into a data table so a generated workbook
demonstrates its own value immediately.

Per section 20 of the original spec: no meaningless "Test 1 / Test 2"
placeholders — this module is the generic mechanism, product code
supplies the realistic content (e.g. "Salary", "Freelance", "Rent").
"""

from __future__ import annotations

from excel_engine.core.cell import CellAddress
from excel_engine.core.worksheet import Worksheet
from excel_engine.exceptions.errors import WorkbookBuildError
from excel_engine.styles.style_manager import StyleManager


def write_demo_rows(
    ws: Worksheet,
    style: StyleManager,
    headers: list[str],
    rows: list[dict[str, object]],
    top_left: str | CellAddress,
) -> None:
    """Write `rows` (a list of {header: value} dicts) starting at
    `top_left`, styled with the input font (blue) since these are
    example *data*, not formulas.
    """
    anchor = top_left if isinstance(top_left, CellAddress) else CellAddress.from_a1(top_left)
    header_index = {header: i for i, header in enumerate(headers)}

    for row_offset, row in enumerate(rows):
        unknown = set(row) - set(headers)
        if unknown:
            raise WorkbookBuildError(f"Demo row has unknown column(s): {sorted(unknown)}")
        for header, value in row.items():
            addr = anchor.offset(rows=row_offset, columns=header_index[header])
            ws.set_value(addr.to_a1(), value)
            ws.raw[addr.to_a1()].font = style.input_font
