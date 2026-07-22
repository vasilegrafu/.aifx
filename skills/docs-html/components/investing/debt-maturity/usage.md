# debt-maturity

_Authoring guidance for the `debt-maturity` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

The maturity wall: how much debt comes due in each year, at what coupon, in
what instrument. Solvency is a timing question before it is a leverage
question — a company at 3x net debt to EBITDA with nothing due for six years is
in a different position from the same company facing a refinancing next spring.

```jinja
{{ c.debt_maturity(
    caption="Term debt maturity profile", unit="$M",
    summary="Weighted average coupon 3.1%, weighted average life 6.4 years. The FY2027 wall of $18,400M refinances at roughly 5.2% on today's curve, costing about $390M of incremental annual interest.",
    items=[
        ("FY2026",  "8,200",  10.0, "2.4%", "Senior notes"),
        ("FY2027", "18,400",  22.4, "1.9%", "Senior notes"),
        ("FY2028", "11,300",  13.7, "3.0%", "Senior notes"),
        ("FY2029",  "9,600",  11.7, "3.3%", "Senior notes"),
        ("FY2030+", "34,800", 42.2, "3.6%", "Notes and green bonds"),
    ]) }}
```

Bar widths come from a `data-pct` attribute read by CSS `attr()` in
Chromium/Edge and applied by `attr-fallback.js` everywhere else; every row also
prints its amount.

Rules: shares are percentages of TOTAL debt and sum to 100%; group everything
beyond five years into a single bucket rather than drawing a twenty-year tail.
State the refinancing cost in `summary` — the wall only matters in relation to
today's curve, and the incremental interest is the number a reader wants.
Include undrawn revolver capacity and cash in `summary` too, since they decide
whether a wall is a problem. Operating leases and pension obligations are not
term debt; if they matter, give them their own table rather than blending them.
