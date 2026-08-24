# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [0.7.0] — Phase 9: Build / Validate / Release Pipeline

**All 9 phases of the original spec are now complete.**

### Added

- `products/registry.py` — `PRODUCTS` dict mapping a CLI product name
  (`"financial_os"`) to its builder function, `ProductConfig`, and
  validation profile (`required_sheets`/`required_tables`). A second
  product means one new entry here — none of the three scripts below
  need to change.
- `products/financial_os/config.py` gained `REQUIRED_SHEETS` /
  `REQUIRED_TABLES`, feeding that registry entry.
- `scripts/build.py` — `python scripts/build.py financial_os`: config
  → build → validate → export, in that order, refusing to write a file
  if validation fails (section 23). Reports **4 real steps** (Load
  config / Build workbook / Validate / Export), not the original
  spec's illustrative 8 — see docs/architecture.md's Phase 9 notes for
  why faking finer-grained progress than the pipeline actually has
  would be theater, not reporting.
- `scripts/validate.py` — `python scripts/validate.py <file.xlsx>
  [--product financial_os]`: loads a built file and prints
  `ValidationReport.format()` (section 24's exact style, already built
  in Phase 7). Exit code reflects pass/fail.
- `scripts/release.py` — `python scripts/release.py financial_os
  [--force]`: build + validate + package into
  `dist/<product-slug>/Product_vX.Y.Z.xlsx` plus `Documentation/`,
  `License/`, `Release/` (section 25's exact structure). Refuses to
  overwrite an existing release of the same version without `--force`
  (section 25: "Do not overwrite previous releases accidentally") —
  the file itself is checked, not just the directory's existence.

### Fixed

- `scripts/build.py`'s first draft printed each step's label *before*
  running the operation (`print(..., end="")` then run then
  `print("done")`), which meant `build_financial_os()`'s own `logger.info`
  calls landed mid-line, corrupting the progress display (e.g.
  `[2/4] Building workbook           2026-08-19 ... INFO ...`). Fixed
  by printing each step as a single line *after* the operation
  completes — engine log lines now appear as their own lines *above*
  the step they belong to, which is both correct and more useful (the
  diagnostic info is still visible, just not interleaved into a
  progress indicator). Found by actually running the script, not by
  reading the code.

### Tests

- `tests/product/test_scripts.py` — 12 tests, split deliberately:
  - Direct function calls for logic that's awkward to force through a
    subprocess: an unknown product name, a validation failure via a
    monkeypatched broken builder registered into `PRODUCTS` (proving
    *nothing* gets exported when validation fails, not just that the
    exit code is non-zero), the overwrite guard refusing and then
    succeeding with `--force`.
  - Real `subprocess.run([sys.executable, "scripts/build.py", ...])`
    calls for the actual CLI entry points — exit codes, stdout content,
    and a full LibreOffice recalculation of the CLI's own output file
    (0 errors, matching Phase 8's own bar).
- **260 tests total**, 95% statement coverage on `src/excel_engine`
- `ruff check` and `mypy --strict` — 0 issues across `src/`, `products/`,
  and the new `scripts/`

## [0.6.0] — Phase 8: Financial OS Product

### Added

**Engine extensions made in service of this product** (not new phases —
gaps Phase 8 exposed in already-built modules, fixed at the source):
- `data.tables.ColumnSchema` gained a `formula` field: same-row
  computed columns (e.g. Investments' `Gain/Loss = {Current Value} -
  {Quantity}*{Purchase Price}`, Goals' `Progress`/`Status`), resolved
  per-row, blank until the trigger column is filled, styled with
  `formula_font`.
- `charts.manager._months_back` promoted to public `months_back` —
  needed by product-level multi-series charts, not just the built-in
  single-table ones.
- `components.tables.add_data_table` and `data.tables.add_typed_table`
  now set real column widths (generic header-length fallback in the
  former, type-aware minimums — e.g. dates need 13+ characters — in the
  latter). **Every typed table built before this fix had no width
  logic at all**; found by looking at a rendered PDF, not by reading
  code — the Income sheet's Date column showed `###`.

**Financial OS**
- `products/financial_os/config.py` — `FINANCIAL_OS_CONFIG`, `MENU_ITEMS`
- `products/financial_os/formulas/financial_metrics.py` — what "Net
  Worth", "Savings Rate", etc. mean (section 2.2: business logic never
  lives in the generic engine)
- `products/financial_os/data/demo_data.py` — realistic rows for every
  sheet (section 20: no "Test 1/Test 2")
- 9 sheet builders under `products/financial_os/sheets/`: Income,
  Expenses, Bills, Investments, Net Worth, Goals, Settings, Reports,
  and Dashboard (KPI grid + 4 charts + Goals progress summary)
- `products/financial_os/product.py` — `build_financial_os()`: the
  full orchestrator (build order, navigation menu, sheet reordering)

### Fixed (found by actually building and inspecting the product, not by review)

1. **The workbook-wide navbar (row 1, added last by `product.py`) was
   silently overwriting hidden Dashboard helper cells placed at row 1.**
   `Total Assets`/`Total Liabilities` (feeding the Net Worth KPI) sat at
   `T1`/`U1`; the "Goals" nav item's merged range happened to land on
   `S1:U1`, wiping `U1`'s formula the moment the navbar was added.
   Fixed by moving those helper cells to row 3+ (row 1 is now
   documented as globally reserved). Caught by checking actual computed
   values against hand math, not by the recalc harness — the formula
   was syntactically fine, it just wasn't there anymore.
2. **Net Worth was summing every historical snapshot ever logged,
   not just the current one.** `total_assets_formula`/
   `total_liabilities_formula` used a plain `SUMIFS(..., Type, "Asset")`
   with no date filter, so July's and August's snapshots got added
   together — a meaningless number, since Net Worth is a point-in-time
   figure, not a running total (unlike Income/Expenses, which correctly
   *are* summed). Fixed with `SUMIFS(..., Date, MAX(Date))`, verified
   empirically in isolation first (a bare `MAX(...)` sub-formula as a
   SUMIFS criteria does work, cross-sheet, once the cross-sheet
   reference itself was written correctly — an earlier version of the
   isolated test was checked against the wrong sheet and looked broken
   when the technique was actually fine).
3. Missing column widths (see "Engine extensions" above) — a real
   visual defect, not just a missing test.

### Tests

- `tests/product/test_financial_os.py` — 9 tests: all 9 sheets present,
  full `validate_workbook()` pass, 0-error recalculation across 147
  formulas, **exact hand-calculated KPI values** (Net Worth, Monthly
  Income/Expenses, Savings, Savings Rate, Investments, Debt, Reports'
  all-time totals) locked in against the demo data, Investments'
  Gain/Loss and Goals' Progress/Status computed-column correctness,
  protection state, and navigation presence on every sheet.
- 1 new regression test in `test_typed_tables.py` for the column-width
  fix.
- The Dashboard was rendered to PDF and visually inspected twice (once
  before, once after the two data bugs above) — the Cash Flow,
  Expense Breakdown, Investment Allocation, and Net Worth Trend charts
  all show correct shapes and proportions matching hand-calculated
  demo data.
- **248 tests total**, 95% statement coverage on `src/excel_engine`
- `ruff check` and `mypy --strict` — 0 issues on both `src/` and the
  new `products/` tree

## [0.5.0] — Phase 7: Validation Engine

### Added

- `excel_engine.validation.report` — `ValidationIssue`, `ValidationResult`
  (passes iff no `error`-severity issues), `ValidationReport`
  (`.passed`, `.all_issues`, `.format()` — renders in the style of
  section 24's `validate.py` output). Not one of the 4 files the
  original spec lists under `validation/`, but necessary shared data
  model for all of them.
- `excel_engine.validation.structure_validator` — `validate_structure`:
  required sheets, required tables (per sheet), required named ranges
- `excel_engine.validation.formula_validator` — `validate_formulas`:
  expected formula cells present; every `Table[Column]` and
  `Sheet!range` reference found in *any* formula in the workbook
  resolves to a real table/column/sheet; flags literal `#REF!` tokens.
  Regex-based, not a full parser — scoped to the two reference shapes
  this engine's own formula builders produce.
- `excel_engine.validation.integrity_validator` — `validate_integrity`
  (duplicate table names workbook-wide, invalid hyperlinks via Phase
  6's scanner, invalid table ranges) and `validate_protection`
  (declared-locked formula cells are actually locked, declared-unlocked
  input ranges are actually unlocked). No dedicated
  `protection_validator.py` in the original spec's file tree, so
  protection checks live here.
- `excel_engine.validation.workbook_validator` — `validate_workbook`:
  runs all four and returns one `ValidationReport`. The CLI wrapper
  (`scripts/validate.py`, argv → file → printed report) is Phase 9's
  job; this is the engine underneath it.

### Fixed (found while building this phase's tests, not in older code)

- Two bugs in this phase's own first draft, both from the same wrong
  assumption: `Worksheet.tables.items()` returns `(name, ref_string)`
  pairs, **not** `(name, Table_object)` — `formula_validator.py` and
  `integrity_validator.py` both initially called `.ref` on what turned
  out to be a plain string. Fixed by using the ref string directly.
- A test bug, not an engine bug: the "duplicate table names" test tried
  to build the duplicate through this engine's own `add_typed_table`
  twice — but openpyxl's `add_table` already refuses a duplicate name
  workbook-wide, so that path can never actually produce the scenario.
  Rewritten to simulate the one place it's still possible (a workbook
  loaded from an externally-edited file) by inserting two `Table`
  objects directly into two sheets' table lists, bypassing the
  normal `add_table` guard — plus a second test that documents the
  guard itself (`add_typed_table` raises on a real duplicate).

### Tests

- 38 new tests: `test_validation_report.py`, `test_structure_validator.py`,
  `test_formula_validator.py`, `test_integrity_validator.py`,
  `test_workbook_validator.py`
- 1 new integration test (`test_validation_on_real_dashboard.py`) that
  builds a full dashboard (typed table + protection + KPI card + bar
  chart + navigation menu, same shape as Phase 6's integration test)
  and confirms it **passes** full validation, then separately confirms
  three deliberately-introduced problems (a broken table reference, a
  missing required sheet, a dangling hyperlink) are each caught by the
  *right* category without affecting the others.
- **234 tests total**, 95% statement coverage on `src/excel_engine`
- `ruff check` — 0 issues
- `mypy --strict` — 0 issues

## [0.4.0] — Phase 6: Chart Engine + Navigation Engine + Protection Engine

### Added

**Chart engine**
- `excel_engine.charts.manager` — `ChartSourceTable` (knows how to turn
  itself into openpyxl `Reference` objects), `build_category_source_table`
  (Category|Value, SUMIFS/AVERAGEIFS/COUNTIFS per category — bar/pie/
  doughnut), `build_trend_source_table` (Period|Value, trailing N
  months, date-range SUMIFS — line)
- `excel_engine.charts` — `add_bar_chart`, `add_line_chart`,
  `add_pie_chart`, `add_doughnut_chart`. Every chart is backed by real
  formulas, not a static snapshot — the chart stays correct as
  underlying data changes. Line charts use straight segments + markers
  (`smooth=False`), not curve-smoothing, so the chart never visually
  implies data between months that doesn't exist.

**Navigation engine**
- `excel_engine.navigation.hyperlinks` — `internal_link` (validates the
  target sheet exists *before* building the link), `validate_all_hyperlinks`
  (scans a whole workbook for any internal link — however it was built
  — pointing at a missing sheet)
- `excel_engine.navigation.menu` — `apply_menu_to_all_sheets`: one call
  puts a consistent navbar, with the right page marked active, on every
  page in the menu. Raises before writing anything if the menu
  references a sheet that doesn't exist.

**Protection engine**
- `excel_engine.protection.cells` — `unlock_range`, `lock_range`
- `excel_engine.protection.sheets` — `protect_sheet` (turns on
  protection, explicitly keeps formatting/sorting/AutoFilter allowed),
  `unprotect_sheet`
- `excel_engine.protection.apply_standard_protection` — the common
  one-call workflow: unlock the editable ranges, protect the sheet

### Fixed

- **`data.tables.add_typed_table` crashed with `KeyError: 'list'`
  when building the number-format map** — same shape as a Phase 5 bug,
  now covered directly by `test_typed_tables.py` rather than only
  surfacing when a chart test happened to use a list column.
  *(Caught while building the Phase 6 integration test; fixed in the
  same module Phase 5 introduced it in.)*

### Verified before writing any code (not assumed)

- **openpyxl's `SheetProtection` boolean attributes default to
  "blocked."** Confirmed via openpyxl's own docstring: *"True values
  mean that protection for the object or action is active [...] this
  is the default when protection is active, i.e. users cannot do
  something."* Without explicitly setting `formatCells`/`formatColumns`/
  `formatRows`/`sort`/`autoFilter` to `False`, `protect_sheet` would
  have produced exactly the "unusably restrictive" workbook section 16
  warns against. `test_protect_sheet_does_not_block_formatting_sorting_autofilter`
  guards this directly.
- **Chart output was checked visually, not just "no recalc error."**
  The full-dashboard integration test's workbook was rendered to PDF/PNG
  and inspected — bar, pie, doughnut, and line charts all show correct
  proportions and values matching the underlying demo data by hand
  calculation (e.g. Aug 2026 trend point = ₹4,700 = 3200+1500).

### Tests

- 29 new unit tests: `test_chart_manager.py`, `test_charts.py`,
  `test_navigation_hyperlinks.py`, `test_navigation_menu.py`,
  `test_protection_cells.py`, `test_protection_sheets.py`
- 1 new integration test (`test_full_dashboard_phase6.py`) — a 3-sheet
  workbook (Orders with a protected typed table, Goals, Dashboard with
  1 KPI card + all 4 chart types), navigation menu applied to every
  sheet, hyperlinks validated, saved, recalculated via LibreOffice (0
  errors on 16 formulas), and separately rendered to images for a
  visual check
- **196 tests total**, 95% statement coverage on `src/excel_engine`
- `ruff check` — 0 issues
- `mypy --strict` — 0 issues

## [0.3.0] — Phase 5: Formula Engine + Data Engine

### Added

**Formula engine**
- `excel_engine.formulas.references` — `table_column`, `sheet_range`,
  `quote_criteria` (escapes embedded `"`), `named_range`
- `excel_engine.formulas.functions` — one builder per supported Excel
  function: `sum_`, `count`, `counta`, `average`, `max_`, `min_`,
  `sumifs`, `averageifs`, `countifs`, `if_`, `iferror`, `index_match`,
  `percentage_of_total`, `growth`, `variance`. All the `IFERROR`-wrapped
  ones default `safe=True`.
- `excel_engine.formulas.Formula` — the public builder, e.g.
  `Formula.sum("Income", "Amount")` → `=SUM(Income[Amount])`.
  Table-backed methods (`sum`, `average`, `count`, `counta`, `max`,
  `min`, `sumifs`, `averageifs`, `countifs`, `index_match`) build
  structured references; `_range` variants are the plain-A1 fallback.
- **XLOOKUP intentionally not implemented** — empirically tested
  against this project's LibreOffice recalc harness and returned
  `#NAME?`. `Formula.index_match` is the supported lookup (also tested,
  computes correctly).

**Data engine**
- `excel_engine.data.validation` — `add_dropdown`, `add_number_range`,
  `add_date_range`, `add_required` (custom non-blank rule, works for
  any cell type)
- `excel_engine.data.named_ranges` — `add_named_range`,
  `list_named_ranges`, `get_named_range_formula`
- `excel_engine.data.demo_data` — `write_demo_rows`: realistic example
  rows (not "Test 1/Test 2"), styled with the input font
- `excel_engine.data.tables` — `ColumnSchema`, `TypedTable`,
  `add_typed_table`: column-typed table (text/number/currency/percent/
  date/list) on top of `components.add_data_table`, wiring in number
  formats and dropdown validation automatically

### Changed

- **`excel_engine.llm.builder` refactored to use the Phase 5 formula
  engine**, as promised when it was added: the local `_kpi_formula` /
  `_TableMeta` stand-in is gone, replaced by a plain dict mapping each
  `KPISpec.agg` value straight onto `Formula.sum` / `.average` / `.count`
  / `.counta` / `.max` / `.min`. KPI formulas now read
  `=SUM(Orders[Amount])` (structured references) instead of
  `='Orders'!$C$2:$C$51` (plain ranges) — both compute identically, but
  structured references are what the original spec's own formula-engine
  example (section 11) asked for.

### Fixed

- **`ExcelWorkbook.sheet_names` now reflects real tab order** after
  `reorder_sheet()` — previously read a stale internal dict. Found
  because `llm.builder` (the first caller to depend on reordering)
  failed a test. New regression test in `tests/unit/test_workbook.py`.
  Benefits every phase, not just the LLM bridge.
- `data.tables.add_typed_table` crashed with `KeyError: 'list'` when
  building the number-format map — "list" columns hold text options,
  not a number, so they needed their own (`"General"`) entry. Caught
  immediately by `test_typed_tables.py`.

### Tests

- 54 new tests: `test_formula_references.py`, `test_formula_functions.py`,
  `test_formula_builder.py`, `test_data_validation.py`,
  `test_named_ranges.py`, `test_demo_data.py`, `test_typed_tables.py`,
  plus one integration test
  (`test_formula_engine_recalculates.py`) that builds a real workbook
  using typed tables + demo rows + seven different `Formula`-built
  formulas (including `SUMIFS` with quoted criteria and `INDEX/MATCH`),
  saves it, recalculates it with LibreOffice, and checks both "0
  errors" *and* the actual computed values match hand-calculated
  expectations.
- Updated `test_llm_builder.py` and the LLM integration test for the
  new structured-reference formula text; re-ran the LibreOffice recalc
  check to confirm the refactor didn't change correctness.
- **167 tests total**, 94% statement coverage on `src/excel_engine`
- `ruff check` — 0 issues
- `mypy --strict` — 0 issues

## [0.2.0] — LLM Bridge (added, beyond the original 9 phases)

### Added

- `excel_engine.llm.schema` — `WorkbookSpec` (Pydantic): the *only*
  shape an LLM is ever allowed to produce. Validates theme name, unique
  sheet names, and that every KPI's `source_sheet`/`source_column`
  actually exists among the tables defined in the same spec.
- `excel_engine.llm.builder` — `build_from_spec(spec) -> ExcelWorkbook`:
  pure, offline, no network. Builds dashboard + KPI cards + data tables
  using only Phase 1–4 components. A small local `_kpi_formula` helper
  stands in for Phase 5's not-yet-built formula engine.
- `excel_engine.llm.client` — `get_workbook_spec(prompt)`: the only
  module in the engine that calls the network (Claude API, via the
  `anthropic` SDK, forced tool-use so the model can only emit a
  `WorkbookSpec`, never free-form text/code). `parse_tool_response` is
  split out as a pure function so response-parsing is unit-testable
  without an API key.
- `excel_engine.llm.generate` — `generate_workbook(prompt)` end-to-end
  helper, plus a CLI: `python -m excel_engine.llm.generate "..."`.
- New optional dependency group: `pip install -e ".[llm]"` (just
  `anthropic`). The core engine has zero dependency on this package or
  on network access.
- `.env.example` gained `ANTHROPIC_API_KEY` and `EXCEL_ENGINE_LLM_MODEL`
  (optional, only read by `excel_engine.llm`).

### Fixed

- **`ExcelWorkbook.sheet_names` now reflects real tab order.** It
  previously read from an internal insertion-ordered dict and silently
  went stale after `reorder_sheet()` — found because `llm.builder` (the
  first caller to actually depend on reordering) failed a test. New
  regression test: `test_sheet_names_reflects_reorder` in
  `tests/unit/test_workbook.py`. This fix benefits every phase, not
  just the LLM bridge.

### Tests

- 21 new tests: `test_llm_schema.py` (validation rules),
  `test_llm_builder.py` (offline spec → real workbook → correct
  formulas/number formats/tables), `test_llm_client.py` (response
  parsing + missing-API-key guard, via a fake tool-use block — no
  network), and one integration test
  (`test_llm_pipeline_recalculates.py`) that runs a fully offline,
  hand-built `WorkbookSpec` through the real builder, saves it, and
  recalculates it with LibreOffice to confirm the formulas actually
  compute — 0 errors.
- **113 tests total**, 93% statement coverage on `src/excel_engine`
- `ruff check` — 0 issues
- `mypy --strict` — 0 issues (one narrow, documented
  `# type: ignore[call-overload]` on the single `anthropic` API call,
  where the SDK's TypedDict-union typing is too specific for a plain
  dict literal to structurally match — explained inline in
  `llm/client.py`)

**What this does *not* do yet:** there's no live end-to-end test against
the real Claude API in this repo (would require your own
`ANTHROPIC_API_KEY`) — everything up to that network boundary is tested
for real; the network call itself is the one piece you verify by
running `python -m excel_engine.llm.generate "..."` yourself once a key
is configured.

## [0.1.0] — Phase 1 + Phase 2 + Phase 3 + Phase 4

### Added

**Phase 4 — Components**
- `excel_engine.components.cards` — `add_kpi_card`: label + formula-driven
  value block
- `excel_engine.components.headers` — `add_title_banner` (with optional
  subtitle), `add_section_header`
- `excel_engine.components.tables` — `add_data_table`: real openpyxl
  `Table` with themed header, banding, frozen panes (column-type/formula
  semantics stay a Phase 5 concern, built on top of this)
- `excel_engine.components.inputs` — `add_labeled_input`
- `excel_engine.components.buttons` — `add_button`, with optional
  internal hyperlink to another sheet
- `excel_engine.components.navbar` — `add_navbar`: row of internal
  sheet links, active item shown bold/un-linked
- `excel_engine.components.progress` — `add_progress_bar`: themed
  conditional-format data bar
- `excel_engine.components.footers` — `add_footer`
- `excel_engine.components` package re-exports all of the above
- 3 new `StyleManager` properties added in service of these components:
  `subtitle_font` (caption text over a primary fill), `nav_link_font`,
  `nav_active_font`

### Tests

- 32 new tests across `test_cards.py`, `test_headers.py`,
  `test_tables.py`, `test_inputs.py`, `test_buttons.py`, `test_navbar.py`,
  `test_progress.py`, `test_footers.py`, and
  `test_style_manager_phase4_fonts.py`
- 1 new integration test (`test_dashboard_components_integration.py`)
  composing every Phase 4 component into one real 3-sheet workbook,
  saved and reloaded with raw openpyxl to confirm it all actually works
  together, not just in isolation
- **92 tests total**, 94% statement coverage on `src/excel_engine`
- `ruff check` — 0 issues
- `mypy --strict` — 0 issues

Three more real bugs caught by these tests and fixed (not left broken
behind a passing-looking stub):
1. `openpyxl.formatting.rule` conditional formatting ranges are read
   back via `.sqref`, not by stringifying the rule object itself.
2. A single-cell conditional-formatting range (`"B2:B2"`) normalizes to
   `"B2"` (no colon) after a real save/reload round-trip through the
   `.xlsx` — an in-memory-only check would have missed this.
3. (Carried from Phase 3, still relevant to this phase's components)
   unset `Border` sides are `None`, not a `Side(style=None)`.

## [0.1.0] — Phase 1 + Phase 2 + Phase 3

### Added

**Phase 3 — Design System**
- `excel_engine.styles.colors` — `ColorPalette` (validated 6-digit hex),
  `THEME_PALETTES` registry with real palettes for `premium`, `minimal`,
  `classic`
- `excel_engine.styles.fonts` — `FontSpec`, `Typography` (title →
  caption size/weight scale)
- `excel_engine.styles.borders` — `build_border`, `box`, `bottom_only`
  presets
- `excel_engine.styles.fills` — `solid_fill`, `NO_FILL`
- `excel_engine.styles.alignment` — `CENTER`/`LEFT`/`RIGHT`/`WRAP`,
  `indented(...)`
- `excel_engine.styles.style_manager` — `StyleManager.for_theme(name)`,
  the single entry point exposing theme-aware `title_font`,
  `header_font`, `kpi_label_font`, `kpi_value_font`, `input_font`
  (always blue), `formula_font`, `header_fill`, `card_fill`,
  `thin_border`, and alignment shortcuts; plus `Spacing` (abstract
  layout scale for Phase 4 components)
- `excel_engine.styles` package now re-exports `StyleManager`/`Spacing`

### Tests

- 31 new tests: `test_colors.py`, `test_fonts.py`, `test_borders.py`,
  `test_fills.py`, `test_alignment.py`, `test_style_manager.py`
  (parametrized across all 3 themes), plus one integration test proving
  `ProductConfig.theme.name → StyleManager → real styled .xlsx` actually
  round-trips through openpyxl on disk
- **60 tests total**, 90% statement coverage on `src/excel_engine`
- `ruff check` — 0 issues
- `mypy --strict` — 0 issues

Two real bugs were caught and fixed by these tests during development
(not left as `pass`/TODO): an unset `Border` side is `None`, not a
`Side` with `style=None`; openpyxl's `Color.rgb` is stored as an
8-digit `"00" + hex` string, not a bare 6-digit hex.

## [0.1.0] — Phase 1 + Phase 2

### Added

**Phase 1 — Foundation**
- `pyproject.toml` with runtime/dev dependencies, pytest/ruff/mypy config
- `requirements.txt`, `requirements-dev.txt`
- Full target directory tree (`src/excel_engine`, `products/financial_os`,
  `tests`, `assets`, `templates`, `docs`, `scripts`, `output`)
- `excel_engine.logging_config` — centralized logging setup
- `excel_engine.exceptions.errors` — typed exception hierarchy
  (`ExcelEngineError` and 7 subclasses)
- `excel_engine.config.product_config` — `ProductConfig`, `LocaleConfig`,
  `ThemeConfig` (Pydantic v2), including `ProductConfig.from_yaml(...)`
- `excel_engine.config.settings` — `EngineSettings` loaded from env vars
- `excel_engine.config.themes` — theme-name registry

**Phase 2 — Core Excel Engine**
- `excel_engine.core.cell` — `CellAddress`, A1 parsing, column
  letter/index conversion
- `excel_engine.core.range` — `CellRange`, A1 range parsing, sheet-qualified
  references
- `excel_engine.core.metadata` — `WorkbookMetadata`, maps onto openpyxl
  document properties
- `excel_engine.core.worksheet` — `Worksheet`, typed wrapper (values,
  formulas, merge, column width, row height, freeze panes, tab color,
  gridlines, print area)
- `excel_engine.core.workbook` — `ExcelWorkbook`, typed wrapper (add/get/
  remove/reorder sheet, save, load)

### Tests

- 29 tests across `tests/unit/` (cell, range, workbook, worksheet, config)
  and `tests/integration/` (end-to-end smoke test building a real,
  reloadable workbook through the typed API only)
- 89% statement coverage on `src/excel_engine`
- `ruff check` — 0 issues
- `mypy --strict` — 0 issues

### Not yet implemented

Everything in the Roadmap table in `README.md` beyond Phase 2: design
system, components (KPI cards/tables/navbar/etc.), formula engine, chart
engine, navigation/protection/validation engines, the Financial OS
product itself, and the build/validate/release scripts. Those packages
exist only as empty, scaffolded directories with an `__init__.py`.
