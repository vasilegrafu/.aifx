# ownership-table

_Authoring guidance for the `ownership-table` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Who owns the company and what they did last quarter. Ownership answers
questions no financial statement does: who can force a change, how much stock
must clear the market if sentiment turns, and whether the people running the
business are buying it.

```jinja
{{ c.ownership_table(
    caption="Largest holders", asof="2026-06-30",
    summary=[("Insider ownership", "0.05%"), ("Institutional", "62.1%"),
             ("Free float", "99.9%"), ("Short interest", "0.8% of float"),
             ("Days to cover", "1.2")],
    note="Source: Form 13F filings for the quarter ended 30 Jun 2026 and Forms 3/4/5. 13F data is 45 days stale by rule.",
    rows=[
        ("Vanguard Group",       "Index",     "1,380M", 9.2, "+0.1pp", "neutral"),
        ("BlackRock",            "Index",     "1,050M", 7.0, "+0.2pp", "neutral"),
        ("Berkshire Hathaway",   "Strategic", "300M",   2.0, "-1.4pp", "bad"),
        ("State Street",         "Index",     "615M",   4.1, "0.0pp",  "neutral"),
        ("Insiders and officers", "Insider",  "7M",     0.05, "-0.01pp", "neutral"),
    ]) }}
```

Rules: date the table and say where the data came from — 13F filings are 45
days stale by rule and a reader who does not know that will misread a change
column. Separate index holders from active and strategic ones: a Vanguard stake
carries no information about the business, and treating it as conviction is the
most common misreading of this table. `tone` marks whether a change matters to
the thesis, not its sign. Include short interest and days to cover in `summary`
where they are material. Insider buying is far more informative than insider
selling, which has many innocent explanations — say which kind you are looking
at.
