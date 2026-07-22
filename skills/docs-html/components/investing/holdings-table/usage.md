# holdings-table

_Authoring guidance for the `holdings-table` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

Every position in the portfolio with its weight drawn as a bar, then whatever
columns the review needs — cost, price, value, unrealised, contribution. The
bar makes concentration visible at a glance, which a column of percentages
never does.

```jinja
{{ c.holdings_table(
    caption="Portfolio — 30 Jun 2026",
    headers=["Avg cost", "Last", "Value", "Unrealised", "Contribution YTD"],
    rows=[
        ("Apple (AAPL)",        18.4, ["$164.20", "$232.40", "$184,300", "+41.5%", "+3.1pp"], "good"),
        ("Microsoft (MSFT)",    14.1, ["$318.00", "$428.10", "$141,200", "+34.6%", "+2.4pp"], "good"),
        ("Alphabet (GOOGL)",     9.8, ["$142.60", "$186.30", "$ 98,100", "+30.6%", "+1.5pp"], "good"),
        ("Cash",                 7.2, ["—",       "—",       "$ 72,000", "—",      "0.0pp"],  "neutral"),
    ],
    total_row=("Total", "100.0%", ["", "", "$1,001,000", "+22.4%", "+9.6pp"])) }}
```

The weight bar width comes from a `data-pct` attribute (the contract forbids
`style=`), consumed by CSS `attr()` in Chromium/Edge and applied by
`attr-fallback.js` everywhere else; the numeric percentage sits beside the bar.

Rules: weights sum to 100% including cash — cash is a position and hiding it
overstates every other weight. Same valuation date for every row, named in the
caption. `tone` colors only the LAST column, so put the number that carries the
verdict there (unrealised or contribution, not both). Sort by weight
descending; concentration is the point of the picture. More than about twenty
rows belongs in `wide` mode or a grouped child document.
