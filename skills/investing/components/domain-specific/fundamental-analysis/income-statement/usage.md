# income-statement

_Authoring guidance for the `income-statement` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The income statement as an investor reads it: several periods side by side, the
mandatory subtotal ladder intact, and common-size margin lines under the
subtotals that matter. Line kinds carry the structure — `section` heads a
group, `detail` is an indented component line, `subtotal` rules above,
`total` closes with a double rule, and `pct` renders a muted common-size line.

```jinja
{{ c.income_statement(
    caption="Consolidated statements of operations", unit="$M",
    source="FY2025 Form 10-K, page 31.",
    periods=["FY2023", "FY2024", "FY2025"],
    rows=[
        ("Revenue",                 [],                                    "section",  ""),
        ("Products",                ["298,085", "294,866", "307,000"],     "detail",   ""),
        ("Services",                ["85,200",  "96,169",  "109,200"],     "detail",   ""),
        ("Total net sales",         ["383,285", "391,035", "416,200"],     "subtotal", "2"),
        ("Total cost of sales",     ["(214,137)", "(210,352)", "(219,800)"], "subtotal", ""),
        ("Gross profit",            ["169,148", "180,683", "196,400"],     "subtotal", ""),
        ("Gross margin",            ["44.1%",   "46.2%",   "47.2%"],       "pct",      ""),
        ("Operating income",        ["114,301", "123,216", "134,100"],     "subtotal", ""),
        ("Provision for income taxes", ["(16,741)", "(29,749)", "(22,900)"], "",       "5"),
        ("Net income",              ["96,995",  "93,736",  "111,600"],     "total",    ""),
        ("Net margin",              ["25.3%",   "24.0%",   "26.8%"],       "pct",      ""),
    ]) }}
```

Rules: three periods minimum — one period is a snapshot, not an income
statement, and a trend is what the reader is buying. State the unit ONCE in
`unit`, never per cell. Negatives use accounting parentheses, `(1,234)`; the
component tints them from the leading bracket or minus sign. Never break the
ladder: every subtotal that a reader would compute must be present, so gross
profit and operating income are rows, not something to be inferred. `pct` lines
go directly under the subtotal they describe. Non-GAAP figures are a SEPARATE
labelled block, never mixed into the statutory ladder. `note` numbers link to
`footnote_disclosures` — cite the note on any line whose composition is not
obvious. `source` names the filing and page.

Use `financial_table` (business category) instead for a single-period statutory
statement with no trend and no note references.
