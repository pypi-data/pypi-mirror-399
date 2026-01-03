# excelminer

`excelminer` extracts Excel workbook artifacts into a small, normalized in-memory graph (nodes + edges) that you can serialize to deterministic JSON.

It is designed for inventory, analysis, and reproducible diffs (stable ordering), not for “opening Excel” or evaluating formulas.

## What you can extract

From OOXML files (`.xlsx/.xlsm/.xltx/.xltm`) without Excel installed:

- sheets
- defined names
- connections + basic source inference
- Power Query queries (when stored as `xl/queries/*.xml`)
- Power Query mashup-container detection (best-effort, metadata-only)
- pivot tables + pivot caches (best-effort)
- VBA project presence for macro-enabled OOXML (`.xlsm/.xltm/.xlam`) (metadata-only)
- formula text + basic dependencies (via `openpyxl`, when enabled)

Optional enrichment:

- used-range “value blocks” via calamine (fast scanning)
- Windows Excel COM automation (for legacy formats like `.xls/.xlsb` and opt-in enrichment for modern OOXML)

## Install

Base install:

```bash
pip install excelminer
```

Optional extras:

```bash
pip install "excelminer[calamine]"  # pandas + python-calamine
pip install "excelminer[com]"       # Windows + Microsoft Excel required
```

## Quickstart

### JSON output

```python
from excelminer import AnalysisOptions, analyze_to_dict

result = analyze_to_dict(
    "workbook.xlsx",
    options=AnalysisOptions(include_formulas=True),
)

print(result["graph"]["stats"])          # counts by node kind
print(result["reports"][0]["backend"])    # per-backend reports
```

### Graph output

```python
from excelminer import AnalysisOptions, analyze_workbook

graph, reports, ctx = analyze_workbook(
    "workbook.xlsx",
    options=AnalysisOptions(include_formulas=True),
)

print(graph.stats())
print([r.backend for r in reports])
print(ctx.issues)
```

## Output shape (high level)

`analyze_to_dict()` returns:

- `path`, `options`, `issues`
- `reports`: per-backend stats/issues
- `graph`: `{ nodes: [...], edges: [...], stats: {...} }`

Common node kinds include: `sheet`, `connection`, `source`, `powerquery`, `pivot_table`, `pivot_cache`, `vba_project`, `formula_cell`, `cell_block`.

## Default backend pipeline

By default, backends run in this order:

1. OOXML zip parsing (structure)
2. VBA projects (macro detection for `.xlsm/.xltm/.xlam`)
3. Power Query (queries XML + mashup-container detection)
4. Pivot tables (pivots + caches)
5. Calamine (used-range/value blocks; optional)
6. openpyxl (formula text)
7. Excel COM (Windows-only enrichment; opt-in for modern OOXML)

You can override the pipeline via the `backends=` argument.

## Security & privacy notes

- Connection parsing produces a sanitized key/value view (`password` / `user id` / etc masked) in `connection_kv`.
- The raw connection string may also be stored in `connection.raw`.

Treat the output JSON as potentially sensitive. If you don’t need connections, use `AnalysisOptions(include_connections=False)`.

## Documentation (in this repo)

- docs/README.md: documentation index
- docs/USAGE.md: usage patterns + backend ordering
- docs/OPTIONS.md: `AnalysisOptions` flags and limits
- docs/BACKENDS.md: backend behavior and requirements
- docs/OUTPUT.md: output schema and common node/edge kinds
- docs/SECURITY.md: security & privacy notes
- docs/DEVELOPMENT.md: tests, COM opt-in, coverage profiles

## Development notes

COM integration tests are opt-in because some environments can crash the Python process when Excel COM is invoked.

PowerShell:

```powershell
$env:EXCELMINER_RUN_COM_TESTS='1'
pytest -m integration
```
