# covenant-table

_Authoring guidance for the `covenant-table` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Each financial covenant with its test, its limit, where the company actually
sits, and how much room is left. Covenants are the mechanism by which a slow
deterioration becomes a sudden crisis, so the headroom column — expressed in
the units the business moves in, not in ratio points — is the one that matters.

```jinja
{{ c.covenant_table(
    caption="Senior facility covenants", asof="30 Jun 2026",
    note="Tested quarterly on a rolling twelve-month basis. Headroom is stated as the EBITDA decline that would breach the test, holding debt constant.",
    rows=[
        ("Net leverage",        "Net debt / EBITDA",       "≤ 3.50x", "2.85x", "18% EBITDA decline", "pass"),
        ("Interest cover",      "EBITDA / net interest",   "≥ 3.00x", "3.42x", "12% EBITDA decline", "tight"),
        ("Fixed charge cover",  "EBITDAR / fixed charges", "≥ 1.75x", "2.31x", "24% EBITDA decline", "pass"),
        ("Minimum liquidity",   "Cash + undrawn revolver", "≥ $150M", "$412M", "$262M",              "pass"),
    ]) }}
```

Rules: express headroom as the OPERATIONAL move that would cause a breach —
"an 18% EBITDA decline" is actionable where "0.65x of headroom" is not. State
the test frequency and whether it is rolling or point-in-time; a quarterly
rolling test behaves very differently from an annual one in a downturn. Use the
credit agreement's own definitions, which usually permit add-backs the income
statement does not — if covenant EBITDA differs from reported EBITDA, give the
bridge in `note`, because that gap is often where the real headroom is.
`tight` means inside your own warning threshold, not the lender's; say what your
threshold is. A breach is never reported without the waiver status beside it.
