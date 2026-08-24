# Excel Product Engine

A reusable Python engine for generating production-grade Excel products —
Financial OS, Business Dashboard, CRM, Sales Dashboard, Project Manager,
Inventory Manager, HR Dashboard, and more — from one shared architecture,
without rewriting the core Excel logic per product.

> **Status: all 9 phases complete** — foundation, core engine, design
> system, components, an LLM bridge (optional, beyond the original
> spec), the formula/data engines, charts/navigation/protection, a
> validation engine, the first full product (Financial OS), and the
> build/validate/release CLI pipeline. See "Roadmap" below for what
> landed in which phase, and CHANGELOG.md for the detailed history.
>
> New here? **[docs/user-guide/setup-and-usage-guide.md](docs/user-guide/setup-and-usage-guide.md)**
> walks through setup, generating a workbook, and building a new
> product step by step — this README is the reference, that guide is
> the tutorial.

## Architecture

The engine is deliberately split from any specific product:

```
src/excel_engine/      # product-agnostic engine (this repo's core IP)
  core/                 # ExcelWorkbook / Worksheet / CellAddress / CellRange / WorkbookMetadata
  config/                # ProductConfig, EngineSettings, theme registry (Pydantic)
  exceptions/            # typed exception hierarchy
  logging_config.py       # centralized logging setup
  styles/ components/ formulas/ charts/ data/ navigation/
  protection/ validation/ exporters/     # scaffolded, land in later phases

products/financial_os/  # the FIRST product built on the engine
  sheets/ formulas/ data/                # scaffolded, lands in Phase 8

tests/
  unit/ integration/ product/ regression/
```

The engine never contains business logic like "Net Worth" or "Savings
Rate" — it only knows how to build sheets, KPI cards, tables, charts,
and formulas from configuration. Products (like Financial OS) supply the
meaning; the engine supplies the mechanism.

## Installation

Requires Python 3.12+.

```bash
pip install -e ".[dev]"
```

## Development

```bash
# run tests with coverage
pytest

# lint
ruff check src products scripts tests

# type-check (strict)
mypy src/excel_engine
mypy products scripts --explicit-package-bases
```

All checks currently pass cleanly (260 tests, 95% coverage, 0 lint/type
errors) — see CHANGELOG.md for the exact numbers as of the last update.

## Core workbook API

The foundation everything else builds on — `ExcelWorkbook`/`Worksheet`
typed wrappers over openpyxl, and the config system:

```python
from excel_engine import ExcelWorkbook, WorkbookMetadata

workbook = ExcelWorkbook(metadata=WorkbookMetadata(title="Financial OS"))

dashboard = workbook.add_sheet("Dashboard")
dashboard.set_value("A1", "Financial OS")
dashboard.set_formula("A2", "=1+1")
dashboard.freeze_panes("A3")

workbook.save("output/financial_os.xlsx")
```

Product configuration is validated, typed YAML:

```python
from excel_engine.config.product_config import ProductConfig

config = ProductConfig.from_yaml("products/financial_os/config.yaml")
```

### Financial OS (Phase 8)

The first real product, built entirely from the engine above:

```bash
python -c "from products.financial_os.product import build_financial_os; build_financial_os().save('output/financial_os.xlsx')"
```

9 sheets (Dashboard, Income, Expenses, Bills, Investments, Net Worth,
Goals, Reports, Settings), realistic demo data, 7 live KPI cards, 4
charts (2 of them dual-series/cross-table, built directly with
openpyxl where the generic single-table chart engine doesn't reach —
see docs/architecture.md), computed columns (Investments' Gain/Loss,
Goals' Progress/Status), protected input ranges, and a navigation menu
on every page. Passes full `validate_workbook()` and recalculates with
0 errors across 147 formulas. See `tests/product/test_financial_os.py`
for the numbers this locks in.

### Build / Validate / Release CLI (Phase 9)

The command-line pipeline the rest of this section builds toward:

```bash
python scripts/build.py financial_os      # config -> workbook -> validate -> export
python scripts/validate.py output/Financial_OS_v1.0.0.xlsx
python scripts/release.py financial_os    # build + validate + package into dist/
```

`build.py` never exports a file if validation fails (section 23).
`release.py` refuses to overwrite an existing release of the same
version unless you pass `--force` (section 25), and produces:

```
dist/financial-os/
├── Financial_OS_v1.0.0.xlsx
├── Documentation/README.md
├── License/LICENSE.txt
└── Release/RELEASE_NOTES.txt
```

Reports 4 real, individually-observable build steps (Load config →
Build workbook → Validate → Export) rather than the original spec's
illustrative 8 — see docs/architecture.md for why. Add a second
product by registering it in `products/registry.py`; none of the three
scripts need to change.

### Styling (Phase 3)

A `StyleManager` resolves a theme name into ready-to-use openpyxl
`Font` / `PatternFill` / `Border` / `Alignment` objects, so product and
component code never constructs these by hand or hard-codes hex colors:

```python
from excel_engine.styles import StyleManager

style = StyleManager.for_theme(config.theme.name)  # "premium" | "minimal" | "classic"

cell = dashboard.raw["A1"]
cell.font = style.title_font
cell.fill = style.header_fill
cell.alignment = style.center
```

Every style is theme-aware except `style.input_font`, which is always
blue — matching the universal "blue = user input, black = formula"
spreadsheet convention regardless of theme.

### Components (Phase 4)

Reusable, theme-driven UI building blocks. Each takes a `Worksheet` + a
`StyleManager` and returns the `CellRange` it occupies, so you can stack
them without recomputing row/column math by hand:

```python
from excel_engine.components import add_title_banner, add_kpi_card, add_data_table

add_title_banner(dashboard, style, "Financial OS", subtitle="Auto-calculated", width=9)
add_kpi_card(dashboard, style, "Total Revenue", "=SUM(Orders!C2:C50)",
             top_left="A5", number_format='"₹"#,##0')
add_data_table(orders_sheet, style, ["Date", "Customer", "Amount"],
               n_rows=30, table_name="Orders")
```

Available: `add_title_banner`, `add_section_header`, `add_kpi_card`,
`add_data_table`, `add_labeled_input`, `add_button`, `add_navbar`,
`add_progress_bar`, `add_footer`.

### LLM bridge — generate a workbook from a plain-English prompt

Optional layer on top of everything above. You describe the workbook in
plain English; Claude turns that into a validated, constrained
`WorkbookSpec` (never raw code); the same deterministic builder used
everywhere else turns that into a real `.xlsx`.

```bash
pip install -e ".[llm]"
cp .env.example .env        # then fill in ANTHROPIC_API_KEY

python -m excel_engine.llm.generate "Make me a sales tracker with total revenue, average order value, and total orders, tracking Date, Customer, and Amount"
```

Or from Python:

```python
from excel_engine.llm import generate_workbook

path = generate_workbook("Make me a sales tracker with total revenue and total orders")
```

**How it stays safe:** the LLM can only ever emit a `WorkbookSpec`
(Pydantic-validated: known theme, unique sheet names, every KPI's
source column checked against its table's real columns) — it never
writes Python, never touches openpyxl, and can't reference a sheet or
column that doesn't exist. `excel_engine.llm.builder` is pure and fully
testable offline; `excel_engine.llm.client` is the only module in the
whole engine that makes a network call.

### Formula engine (Phase 5)

`Formula` builds correct, safe formula strings so nothing hand-
concatenates Excel syntax:

```python
from excel_engine.formulas import Formula

Formula.sum("Income", "Amount")                                    # =SUM(Income[Amount])
Formula.sumifs("Orders", "Amount", ("Colorway", "Saddle Amber"))    # =SUMIFS(Orders[Amount], Orders[Colorway], "Saddle Amber")
Formula.average("Orders", "Amount")                                  # =IFERROR(AVERAGE(Orders[Amount]), 0)
Formula.index_match("Income", "Amount", '"Salary"', "Income", "Source")
Formula.growth("B2", "B1")                                            # period-over-period growth
```

`Formula.sum(...)` etc. build **structured table references**
(`Table[Column]`) and require the table to be a real Excel Table (e.g.
via `data.tables.add_typed_table` below). Use the `_range` variants
(`Formula.sum_range("Orders", "C2:C50")`) when there's no Table object.
XLOOKUP is deliberately not supported — it was tested against this
project's recalculation harness and failed (`#NAME?`); `index_match`
is the supported lookup.

### Data engine (Phase 5)

Typed columns on top of `add_data_table`, with number formats and
dropdown validation wired in automatically:

```python
from excel_engine.data.tables import ColumnSchema, add_typed_table

table = add_typed_table(
    orders_sheet, style,
    columns=[
        ColumnSchema(header="Date", type="date"),
        ColumnSchema(header="Colorway", type="list", options=("Amber", "Teal")),
        ColumnSchema(header="Amount", type="currency"),
    ],
    n_rows=50, table_name="Orders",
)
```

Also available: `data.validation` (`add_dropdown`, `add_number_range`,
`add_date_range`, `add_required`), `data.named_ranges`
(`add_named_range`, `list_named_ranges`), and `data.demo_data`
(`write_demo_rows` — realistic example rows, not "Test 1/Test 2").

### Charts (Phase 6)

Each chart writes its own small, formula-driven aggregation table (kept
off to the side) so it stays correct as the underlying data changes —
no static snapshots:

```python
from excel_engine.charts import add_bar_chart, add_line_chart, add_pie_chart, add_doughnut_chart

add_bar_chart(
    dashboard, style, "Revenue by Colorway", "Orders", "Colorway", "Amount",
    categories=["Amber", "Teal", "Plum"], anchor_cell="B9", data_top_left="T5",
)
add_line_chart(
    dashboard, style, "Revenue Trend", "Orders", "Date", "Amount",
    anchor_cell="K9", data_top_left="T15", periods=6,
)
```

`categories` must be listed explicitly (no `UNIQUE()` — see
docs/architecture.md). `add_pie_chart`/`add_doughnut_chart` share the
same signature as `add_bar_chart`.

### Navigation (Phase 6)

One call puts a consistent navbar — with each page showing itself as
active — on every sheet in the menu:

```python
from excel_engine.navigation import apply_menu_to_all_sheets, validate_all_hyperlinks

apply_menu_to_all_sheets(workbook, style, ["Dashboard", "Orders", "Goals"])
assert validate_all_hyperlinks(workbook) == []   # catches any link to a missing sheet
```

### Protection (Phase 6)

```python
from excel_engine.protection import apply_standard_protection

apply_standard_protection(orders_sheet, editable_ranges=["A2:C51"])
```

Locks everything except the given ranges, then turns on sheet
protection — without disabling formatting/sorting/AutoFilter (openpyxl
defaults to blocking those too; explicitly re-enabled here so the sheet
doesn't become unusable).

### Validation (Phase 7)

Runs structure, formula, integrity, and protection checks and combines
them into one report — the "did the build actually work" check every
generated workbook should pass before you hand it to someone:

```python
from excel_engine.validation import validate_workbook

report = validate_workbook(
    workbook, product_name="Sales Dashboard",
    required_sheets=["Dashboard", "Orders"],
    required_tables={"Orders": ["Orders"]},
    expected_formula_cells=[("Dashboard", "A6")],
)
print(report.format())
assert report.passed
```

```
========================================
SALES DASHBOARD VALIDATION
========================================

Structure                 PASS
Formulas                  PASS
Integrity                 PASS
Protection                PASS

========================================
STATUS: PASS
========================================
```

The **Formulas** check scans every formula in the workbook and flags
any `Table[Column]` or `Sheet!range` reference pointing at something
that doesn't exist — not just the ones you explicitly declared.
**Integrity** reuses Phase 6's hyperlink scanner, so it also catches
broken links built outside this validator (e.g. by hand). This is
programmatic — the actual `python scripts/validate.py file.xlsx` CLI
(section 24 of the spec) is Phase 9's job; this is the engine under it.

## Roadmap

| Phase | Scope                                              | Status        |
|-------|-----------------------------------------------------|---------------|
| 1     | Foundation: packaging, config, logging, exceptions   | ✅ Done       |
| 2     | Core engine: workbook / worksheet / cell / range     | ✅ Done       |
| 3     | Design system: theme, fonts, colors, style manager   | ✅ Done       |
| 4     | Components: KPI cards, tables, headers, navbar, etc. | ✅ Done       |
| —     | **LLM bridge** (prompt → spec → workbook), optional  | ✅ Done       |
| 5     | Formula engine + data engine (validation, tables)    | ✅ Done       |
| 6     | Chart engine, navigation engine, protection engine   | ✅ Done       |
| 7     | Validators (structure/formula/integrity/protection)  | ✅ Done       |
| 8     | Financial OS product (dashboard + all data sheets)   | ✅ Done       |
| 9     | build.py / validate.py / release.py pipeline         | ✅ Done       |

**All 9 phases complete.** `products/registry.py` maps a CLI product
name to its builder + validation profile, so adding a second product
means one new registry entry — `scripts/build.py`, `validate.py`, and
`release.py` never need to change.

The LLM bridge isn't one of the original 9 phases — it's an added,
optional feature (`excel_engine.llm`, requires `pip install -e ".[llm]"`)
that sits on top of Phases 1–4. It never becomes a dependency of the
core engine or of any future phase.

Each phase, once implemented, gets its own tests (unit + integration),
passes `ruff` and `mypy`, and is documented in `CHANGELOG.md` before the
next phase starts — no phase is marked done without a working, tested
build behind it.

## License

Proprietary — license terms to be finalized. Update `pyproject.toml`'s
`license` field once decided.
