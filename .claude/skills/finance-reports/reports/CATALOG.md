# Reports — catalogue

_Every report, by what it argues. **Generated** from each report's own_
_declarations — do not edit; run `python .claude/skills/finance-reports/reports/catalog_builder.py`._

2 reports. Narrow to a candidate here, then read its `usage.md` for what
it fetches, what that costs, and what its assertions guarantee.

```bash
python .claude/skills/finance-reports/reports/report_builder.py <report> <args...> --out DIR [--asset-bundles local]
```

| report | title | what it argues | arguments | docs |
|---|---|---|---|---|
| `financial-profile` | Financial Profile | where a company's money comes from, where it goes, what it owns, and how that shape changed | `--peers PEERS symbol` | [usage](company/financial-profile/usage.md) |
| `income-statement` | Income Statement | one income statement read all the way down — every published line, the flow that produced the bottom line, and what the source does not reconcile | `--basis {annual,quarter} [--periods PERIODS] symbol` | [usage](company/income-statement/usage.md) |
