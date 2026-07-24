# aging-schedule

_Authoring guidance for the `aging-schedule` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Receivables (or payables) split into ageing buckets, with each counterparty's
overdue share drawn as a bar. Ageing is where revenue quality shows up first:
sales booked to customers who are not paying appear here a year before they
appear in a write-off.

```jinja
{{ c.aging_schedule(
    caption="Trade receivables ageing at 30 Jun 2026", unit="$000",
    buckets=["Current", "1–30 days", "31–60 days", "61–90 days", "90+ days"],
    note="Provision of $840k covers 71% of balances over 90 days. Northwind alone is 46% of the 90+ bucket and is in payment dispute.",
    rows=[
        ("Northwind Traders",  ["1,240", "380", "210", "160", "540"], "2,530", 51.0, "bad"),
        ("Contoso Ltd",        ["3,110", "420", "90",  "0",   "0"],   "3,620", 14.1, "neutral"),
        ("Fabrikam Inc",       ["2,480", "150", "0",   "0",   "60"],  "2,690",  7.8, "good"),
        ("Other (42 accounts)", ["6,900", "820", "310", "120", "570"], "8,720", 20.8, "neutral"),
    ],
    total_row=("Total", ["13,730", "1,770", "610", "280", "1,170", "17,560", ""])) }}
```

Rules: buckets are calendar bands from the DUE date, not the invoice date —
ageing from invoice date flatters every schedule with long payment terms. State
the provision and what share of the 90+ bucket it covers, in `note`: an ageing
schedule without provision coverage is half a disclosure. Concentration matters
more than the total, so name counterparties above your materiality threshold
individually and group the tail. Where a balance is disputed rather than simply
late, say so — the two have different recovery odds. The same structure serves
payables, where a lengthening profile is a liquidity signal rather than a credit
one.
