# bridge

_Authoring guidance for the `bridge` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

The waterfall: how a total got from one value to another, one contribution per
row. The most-used analytical graphic in finance — revenue bridges, EBITDA
bridges, free-cash-flow bridges, net-asset-value bridges, GAAP-to-non-GAAP
reconciliations, and price-target bridges are all this one shape. Anchors
(`start`, `subtotal`, `end`) are measured from the axis floor; `up` and `down`
steps float from the running total, which the component tracks at compose time.

```jinja
{{ c.bridge(
    caption="FY2024 → FY2025 revenue bridge ($M)",
    scale_min=380000, scale_max=425000,
    note="Services contributed 53% of the increase on 26% of the base.",
    steps=[
        ("FY2024 revenue",      391035, "start", "391,035"),
        ("Services growth",      13031, "up",     "+13,031"),
        ("iPhone units",          4200, "up",      "+4,200"),
        ("Pricing and mix",       9134, "up",      "+9,134"),
        ("FX translation",       -1200, "down",    "-1,200"),
        ("FY2025 revenue",      416200, "end",   "416,200"),
    ]) }}
```

Bar offset and width are computed at compose time and carried as `data-lo` /
`data-span` (the contract forbids `style=`), read by CSS `attr()` in
Chromium/Edge and applied by `attr-fallback.js` everywhere else, so the bars are
proportional in every browser. Every row also prints its own value.

Rules: the steps must actually reconcile — start plus every delta equals end, and
you check that by hand before publishing. `scale_min` is the axis floor, NOT
zero: a bridge from 391,035 to 416,200 drawn from zero shows nothing, and one
drawn from 380,000 shows the whole argument. Deltas are signed numbers; `display`
carries the formatted text with its sign. Five to eight steps — a bridge with
fifteen rows is a table. Name the driver, never the accounting line: "Services
growth" beats "increase in revenue". Where a step is an estimate rather than a
disclosed figure, say so in `note`.

Prefer this over a Mermaid `xychart-beta` or an ECharts waterfall whenever the
decomposition itself is the finding, which is nearly always.
