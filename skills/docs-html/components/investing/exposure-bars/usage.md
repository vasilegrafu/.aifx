# exposure-bars

_Authoring guidance for the `exposure-bars` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

One breakdown of the portfolio as labelled bars — by sector, geography, asset
class, currency, factor, or liquidity. Use it wherever the question is "how
much of the book is in X", and the answer has to be compared against a target
or a limit.

```jinja
{{ c.exposure_bars(caption="Sector exposure vs policy limits", items=[
    ("Information technology", 42.3, "limit 40% — over"),
    ("Communication services", 15.1, "limit 25%"),
    ("Health care",            12.6, "limit 25%"),
    ("Consumer discretionary", 11.0, "limit 25%"),
    ("Financials",              8.6, "limit 25%"),
    ("Cash",                    7.2, "range 5–15%"),
    ("Other",                   3.2, ""),
]) }}
```

Bar widths come from a `data-pct` attribute (the contract forbids `style=`),
consumed by CSS `attr()` in Chromium/Edge and applied by `attr-fallback.js`
everywhere else; the percentage is also printed as text.

Rules: one dimension per figure — a chart mixing sectors and geographies
answers neither question. Percentages sum to 100% including cash and "Other".
Sort descending, except where a fixed order carries meaning (credit ratings,
maturity buckets). The `value` slot is where the LIMIT goes: an exposure with
no stated limit cannot be breached, which is how concentration accumulates.
Use `chart_apache_echarts` with a donut instead when the composition itself is the
finding and there are fewer than six slices.
