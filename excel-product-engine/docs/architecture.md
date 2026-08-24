# Architecture

## Guiding split: Engine vs. Product

`src/excel_engine/` is the reusable, product-agnostic core. It is
allowed to know about spreadsheets, cells, sheets, KPI cards, tables,
charts, and formulas — general Excel concepts. It is **never** allowed
to know about "Net Worth" or "Savings Rate" or any other concept that
only makes sense for one specific product.

`products/financial_os/` (and future products such as a Business
Dashboard or CRM) depend on the engine, never the other way around. A
product supplies:
- a `ProductConfig` (name, version, author, locale, theme)
- sheet builders that call into engine components with product-specific
  data/formulas/labels

This keeps the engine reusable across every future product without
rewriting Excel-generation logic each time.

## Why a wrapper around openpyxl, not raw openpyxl everywhere

`openpyxl` is a low-level library — correct, but verbose, and it exposes
implementation details (merged-cell quirks, raw `Worksheet` objects,
string-typed formulas) directly to every caller. `excel_engine.core`
wraps it behind three small types:

- **`CellAddress`** — a validated `(row, column)` pair with A1-notation
  helpers (`from_a1`, `to_a1`, `offset`). Used anywhere code needs to
  reason about "this cell relative to that one" without string-slicing
  A1 references by hand.
- **`CellRange`** — two `CellAddress` corners, with sheet-qualified,
  properly quoted A1 range strings (`'Order Data'!A1:A5`) — this is
  where the "sheet names with spaces must be quoted in formulas" gotcha
  is handled once, centrally, instead of in every formula-building call
  site.
- **`Worksheet`** / **`ExcelWorkbook`** — typed wrappers over
  `openpyxl.worksheet.worksheet.Worksheet` / `openpyxl.Workbook`. Both
  expose a `.raw` escape hatch for the (rare, later-phase) cases where a
  component genuinely needs direct openpyxl access — e.g. inserting a
  chart object — rather than trying to wrap 100% of openpyxl's surface
  area up front.

## Known openpyxl behaviors worth remembering (validated by tests)

- **Merged cells**: only the top-left cell of a merged range holds a
  value; openpyxl turns the rest into `MergedCell` objects whose
  `.value` is always `None`. `test_engine_smoke.py` deliberately writes
  a formula *outside* a merged title banner to demonstrate/guard this.
- **openpyxl does not evaluate formulas.** `ExcelWorkbook.load()` reads
  back exactly what was written (formula text, not a calculated value).
  Any later phase that needs to *verify* formula output (e.g. a
  `WorkbookValidator`) will need an actual calculation engine (e.g.
  LibreOffice headless recalculation) — this is out of scope for the
  Phase 1/2 core engine.
- **The default sheet**: `openpyxl.Workbook()` always creates one sheet
  named `"Sheet"`. `ExcelWorkbook.add_sheet()` quietly repurposes that
  default sheet the first time it's called (verified by
  `test_default_sheet_is_replaced_not_duplicated`), so callers never see
  a stray extra tab in the output file.

## Configuration validation

`ProductConfig` (Pydantic v2) validates:
- semantic version format (`X.Y.Z`)
- theme name against `excel_engine.config.themes.AVAILABLE_THEMES`
- currency code is upper-cased consistently

This means a product with a typo'd theme name or malformed version
fails fast, at config-load time, with a clear Pydantic `ValidationError`
— not silently, three phases later, when a chart tries to look up a
theme color that doesn't exist.

## What's deliberately not built yet

Sections of the original spec that require the above core engine to
exist first — KPI cards/tables/charts, the formula builder,
navigation/protection/validation engines, and the Financial OS product
itself — are intentionally left unimplemented rather than stubbed with
`pass`. An empty method that claims a feature works would be worse than
no method at all. See `README.md`'s Roadmap table and `CHANGELOG.md`
for exact status.

## Phase 3 design decisions

- **Colors vs. components stay separate.** `styles/` only produces
  openpyxl style *objects* (`Font`, `PatternFill`, `Border`,
  `Alignment`). It never touches a `Worksheet` or writes to a cell —
  that's `components/` (Phase 4)'s job. This mirrors the engine/product
  split: `styles/` is "what a card should look like",
  `components/` is "how to actually draw one".
- **`on_primary` instead of hard-coded white.** Every palette defines
  the text color to use *over* its `primary` fill, rather than every
  caller assuming white text always contrasts. Currently all three
  themes use white, but a future light-primary theme can override it
  without touching `StyleManager`.
- **`input_font` ignores the theme on purpose.** Blue-for-input,
  black-for-formula is a spreadsheet-wide convention people expect
  regardless of brand color — `StyleManager.input_font` returns the
  same blue for every theme, verified by
  `test_input_font_is_always_blue_regardless_of_theme`.
- **`Spacing` is intentionally abstract.** Excel has no single "spacing"
  unit (column width is character-width, row height is points). Rather
  than guess the mapping before any component uses it, `Spacing` is a
  plain ordered scale (`XS`..`XXL`); Phase 4 components decide how to
  turn e.g. `Spacing.MD` into an actual row/column offset for their own
  layout.

## Phase 4 design decisions

- **Every component returns the `CellRange` it occupied.** This is the
  layout contract for the whole engine: nothing hard-codes "the next
  component starts at row 12" — callers read the previous component's
  return value and offset from it. `test_dashboard_components_integration.py`
  exercises this by stacking five components on one sheet.
- **`components/tables.py` vs. the future `data/tables.py` (Phase 5).**
  `add_data_table` only handles the *visual* table: header styling,
  banding, freeze panes, a real openpyxl `Table` object. It knows
  nothing about column types, formulas, or dropdown validation — that's
  Phase 5's data engine, which will call into this component rather
  than duplicate its table-creation logic.
- **`buttons.py` vs. `navbar.py`.** `add_button` is the single-cell
  primitive (filled, bordered, optionally linked); `add_navbar` composes
  a *row* of link-styled (not button-filled) cells, since a strip of
  filled buttons across every sheet would be visually heavier than a
  normal navigation bar. Both exist because they serve different UI
  purposes, not because one duplicates the other.
- **Internal hyperlinks are built directly with openpyxl's
  `cell.hyperlink`, ahead of the Phase 6 navigation engine.** This is
  deliberately the simple, uncoordinated version — Phase 6's
  `navigation/hyperlinks.py` is expected to add link *validation* (e.g.
  "does every navbar item actually point at a sheet that exists?")
  across a whole workbook, not to replace this mechanism.

## LLM bridge design decisions (added, beyond the original 9 phases)

- **The LLM never touches openpyxl.** It can only emit a `WorkbookSpec`
  — a Pydantic model with a fixed shape, validated theme, unique sheet
  names, and cross-checked KPI references. `llm.builder` then builds
  that spec using the exact same `excel_engine.components` a human
  developer calls directly. There is no path from "LLM output" to "code
  that runs" — only "LLM output" to "data that gets validated, then
  interpreted by fixed, tested logic".
- **Forced tool-use, not prompted JSON.** `llm.client` calls the Claude
  API with `tool_choice` forcing exactly one call to a tool whose
  `input_schema` is `WorkbookSpec.model_json_schema()`. This is more
  reliable than asking the model to "reply with JSON" in prose, and
  means malformed output is a Pydantic `ValidationError` at a single,
  well-defined boundary rather than a string-parsing failure anywhere
  downstream.
- **The network call is isolated to one function.** `get_workbook_spec`
  in `llm/client.py` is the only place in the entire engine that imports
  `anthropic` or touches the network. `llm/builder.py` (the part that
  actually writes cells) has zero network dependency and is fully
  tested offline, including a LibreOffice recalculation check that the
  generated formulas are actually correct — not just well-formed text.
- **A local, temporary `_kpi_formula` helper, not a new formula
  engine.** Phase 5 doesn't exist yet, so `llm/builder.py` has its own
  small, fixed set of six aggregate-formula patterns (mirroring what
  `KPISpec.agg` allows). This is explicitly a stand-in — when Phase 5's
  formula engine lands, this function should be deleted in favor of it,
  not kept as a second formula-building path.
  **Update (Phase 5): done.** `llm/builder.py` now maps `KPISpec.agg`
  straight onto `Formula.sum`/`.average`/`.count`/`.counta`/`.max`/`.min`
  — see the Phase 5 section below for why those build structured
  references rather than plain ranges.

## Phase 5 design decisions

- **Structured table references (`Table[Column]`) are the default, not
  plain ranges — verified empirically, not assumed.** Earlier phases
  (2 and 4) leaned on explicit `'Sheet'!$A$2:$A$50` ranges partly out
  of untested caution about structured-reference compatibility with
  this project's LibreOffice-based recalc harness. Phase 5 tested this
  directly: `=SUM(Table[Column])` computes correctly, so `Formula`'s
  table-backed methods use it — it's shorter, auto-adjusts if a table
  grows, and matches the original spec's own example
  (`Formula.sum("Income", "Amount")` → `=SUM(Income[Amount])`). The
  `_range` methods remain for when there's no real Table object.
- **XLOOKUP was tested, not just "documented as a compatibility risk."**
  A workbook with `=XLOOKUP(...)` was run through the project's own
  `recalc.py` and came back `#NAME?`. Rather than implement it with a
  caveat nobody would read, it's simply not implemented — `index_match`
  is the one supported lookup, and it was verified to return the
  correct value in the same test.
- **`formulas/` only builds formula *text*; it has no idea whether a
  table or column actually exists.** Checking that (e.g. "does every
  KPI reference a real table/column") is explicitly Phase 7's job
  (`validation/formula_validator.py`) — `formulas/` stays a small,
  pure, dependency-free string-building layer on purpose.
- **`data/tables.py` vs. `components/tables.py`, now that both exist.**
  `components.add_data_table` draws the visual table (unchanged since
  Phase 4). `data.add_typed_table` calls it once and then layers on
  what only *it* knows: which columns are dates vs. currency vs. a
  fixed list of options, so number formats and dropdown validation get
  applied automatically instead of every product re-deriving them.

## Phase 6 design decisions

- **Every chart writes real formulas, never a static snapshot.**
  `charts.manager` builds a small `Category|Value` or `Period|Value`
  helper table using Phase 5's formula engine (SUMIFS/AVERAGEIFS/
  COUNTIFS), then the chart references *that* range. If someone edits
  a row in the source table, every chart reading from it updates —
  there's no "regenerate the chart" step.
- **`ChartSourceTable` is a small, self-contained dataclass, not just
  four loose integers passed around.** It knows how to build its own
  `data_reference()`/`category_reference()` `openpyxl.chart.Reference`
  objects, so `bar.py`/`line.py`/`pie.py`/`doughnut.py` each stay a
  handful of lines: build the table, hand it to the right chart class,
  anchor it.
- **Line-chart date buckets use `formulas.functions` directly, not
  `Formula.sumifs`.** `Formula.sumifs`'s criteria values are always
  quoted as literal strings (correct for `Colorway = "Amber"`, wrong
  for `Date >= DATE(2026,7,1)` — quoting a formula fragment turns it
  into literal text Excel would try to match against, not evaluate).
  The lower `functions` layer takes raw, already-formula-ready criteria
  for exactly this reason — this is why `formulas/` is split into a
  low-level (`functions`/`references`) and high-level (`Formula`) layer
  in the first place.
- **Navigation validation doesn't only check links it built itself.**
  `validate_all_hyperlinks` scans every cell's `hyperlink` attribute on
  every sheet, so it also catches broken links from Phase 4's
  `add_navbar`/`add_button` (which build hyperlinks directly) — one
  validator, not one per link-building code path.
- **Sheet protection semantics were verified against openpyxl's own
  docstring before writing any code**, not assumed from the attribute
  names (`formatCells`, `sort`, etc. read as if `True` might mean
  "allowed"). They don't — see the CHANGELOG's Phase 6 entry for the
  exact docstring and why getting this backwards would have silently
  violated section 16's "don't make it unusably restrictive."

## Phase 7 design decisions

- **The formula validator is a regex scanner, not a formula parser —
  on purpose.** Writing a real Excel formula grammar is a large,
  separate project with poor payoff here: this engine only ever
  *generates* formulas through `formulas.functions`/`Formula`, which
  produce exactly two reference shapes (`Table[Column]` and
  `Sheet!range`). Scoping the validator to those two shapes catches
  every reference this engine's own output can contain, which is the
  actual job — validating arbitrary hand-written Excel formulas from
  any source is a different, much bigger problem this project doesn't
  need to solve.
- **`Worksheet.tables.items()` returns ref strings, not Table objects —
  found the hard way, not from documentation.** Two modules in this
  phase were written against the wrong assumption on the first pass;
  both broke on the very first real test run. Fixed by using the ref
  string `.items()` already provides, rather than a second lookup.
  Left in the CHANGELOG rather than quietly fixed, since it's exactly
  the kind of openpyxl-specific surprise this project's testing
  discipline exists to catch before it reaches a generated product.
- **Protection validation needs the caller to declare intent.** There's
  no way to look at a built workbook and infer "this cell is *supposed*
  to hold a formula" versus "this cell is *supposed* to be user input"
  — both are just cells with values. `validate_protection` takes
  explicit `expected_locked_formula_cells` / `expected_unlocked_input_ranges`
  rather than guessing, so a real mismatch (not a false alarm) is what
  gets reported.
- **No `protection_validator.py` file, by design, matching the
  original spec's own file tree.** Section 21 lists Protection as a
  fourth check category, but section 3's `validation/` directory only
  lists three validator files. Rather than invent a file the spec
  didn't ask for, `validate_protection` lives in
  `integrity_validator.py` — protection state being wrong is treated as
  one more kind of workbook-integrity problem.

## Phase 8 design decisions

- **Row 1 is now a reserved region, workbook-wide, and it's documented
  as one.** Every sheet gets its navbar added *last*, by `product.py`,
  after every sheet builder has already run — which means any sheet
  builder that writes to row 1 for its own purposes is one navbar-width
  choice away from silent data loss (see the CHANGELOG's Phase 8 bug
  #1). Financial OS's own dashboard.py now keeps everything at row 3+;
  a future phase could make this a build-time check
  (`validation.integrity_validator`) rather than a documented
  convention people have to remember.
- **Net Worth is a snapshot, not a ledger — and the formula has to say
  so explicitly.** Income and Expenses are correctly *summed* across
  every row ever logged. Net Worth looks structurally identical (a
  dated table of amounts) but means something different: it's "what is
  true right now," so summing every historical entry silently produces
  a number with no real meaning. There's no way to catch this class of
  bug with `validate_workbook()` — it's not a broken reference or a
  missing sheet, it's a *correct formula computing the wrong thing*.
  The only defense is what caught it here: checking actual output
  numbers against hand math, not just checking for the absence of
  errors.
- **Two charts (Cash Flow, Net Worth Trend) needed direct openpyxl
  access, and that's fine.** `charts.manager` is deliberately scoped to
  one source table per chart (see its Phase 6 design notes). A 2-series
  Income-vs-Expenses comparison and a cross-table Assets-minus-
  Liabilities trend both fall outside that scope. Rather than force the
  generic engine wider for two specific needs, `sheets/dashboard.py`
  builds them directly against `ws.raw`, the same escape hatch
  `Worksheet.raw`'s own docstring describes. If a third product needs
  the same shape of chart, that's the signal to generalize
  `charts.manager` — not before.
- **Demo data dates are anchored to the real "today"
  (August 2026), not arbitrary placeholder dates.** The Dashboard's
  "Monthly Income"/"Monthly Expenses" KPIs are genuinely dynamic
  (`TODAY()`-driven, recalculating correctly whenever the file is
  reopened) rather than a value baked in at generation time. That only
  demonstrates real data on the day this file was built if the demo
  data's most recent rows fall in the actual current month — so they
  do, on purpose, not by coincidence.

## Phase 9 design decisions

- **4 real build steps, not the spec's illustrative 8.** Section 39
  shows `[1/8]` through `[8/8]` — Load/Workbook/Data model/Formulas/
  Components/Charts/Validate/Package. This engine's sheet builders
  create a sheet's table, formulas, components, and charts together in
  one function call, not as separate global passes over the whole
  workbook (that's a better architecture for the reasons in this
  file's Phase 4/6 notes — table creation and chart creation for the
  *same sheet* have no reason to happen in two different global
  sweeps). `scripts/build.py` reports the granularity that's actually
  true from the caller's side: Load config, Build workbook, Validate,
  Export. Printing 8 checkmarks for phases that don't run as 8
  separate, individually-timed operations would be exactly the kind of
  fake progress reporting this project has avoided since Phase 1's "no
  fake implementations" rule — a real 4-step report beats a fabricated
  8-step one.
- **The product registry is the thing that makes `build.py`/
  `validate.py`/`release.py` generic**, even though only one product
  exists today. Each script takes a product *name* and looks it up —
  none of them import `financial_os` directly. Adding a Business
  Dashboard or CRM product later is one new `ProductRegistration` entry
  in `products/registry.py`; the three scripts are already correct for
  it.
- **`release.py`'s overwrite guard checks the actual target file, not
  just whether the release directory exists.** A directory existing
  (from a previous, different version) shouldn't block a new version's
  release; a matching version's file existing should. Checking
  `xlsx_path.exists()` rather than `release_dir.exists()` gets this
  right without extra bookkeeping.
- **Progress lines print *after* each step, as one atomic statement —
  found necessary by running the script, not by reasoning about it in
  advance.** A `print(label, end="")` / do work / `print("done")`
  pattern seems reasonable until the work being timed calls
  `logger.info()` partway through, and that output lands mid-line. The
  fix (print the whole step line only once the step is actually done)
  is simple, but it was a real bug in the first draft, not a
  theoretical concern — see the CHANGELOG's Phase 9 entry.
