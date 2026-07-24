# dcf-summary

_Authoring guidance for the `dcf-summary` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The discounted cash flow build in one table: projected free cash flow, its
present value, the terminal value, then the bridge from enterprise value down to
equity value per share. Uses the same line grammar as the statements
(`section` / `detail` / `subtotal` / `total` / `pct`), and opens with the
assumption strip — because a DCF without its assumptions on the same page is
an unfalsifiable number.

```jinja
{{ c.dcf_summary(
    caption="Discounted cash flow — value per share", unit="$M except per share",
    assumptions=[("WACC", "8.5%"), ("Terminal growth", "3.0%"),
                 ("Forecast horizon", "5 years"), ("Tax rate", "17.0%"),
                 ("Valuation date", "2026-07-17")],
    periods=["FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"],
    note="Terminal value is 71% of enterprise value — the conclusion rests on the exit assumption, not the forecast.",
    rows=[
        ("Free cash flow",            ["118,400", "124,900", "131,200", "137,100", "142,600"], "",         ""),
        ("Discount factor",           ["0.922",   "0.850",   "0.783",   "0.722",   "0.665"],   "detail",   ""),
        ("Present value of FCF",      ["109,165", "106,165", "102,730", "98,986",  "94,829"],  "detail",   ""),
        ("Sum of present values",     ["511,875"],                                             "subtotal", ""),
        ("Present value of terminal value", ["1,259,000"],                                     "subtotal", ""),
        ("Enterprise value",          ["1,770,875"],                                           "subtotal", ""),
        ("Less: net debt",            ["(51,000)"],                                            "detail",   "12"),
        ("Equity value",              ["1,821,875"],                                           "subtotal", ""),
        ("Diluted shares (M)",        ["14,948"],                                              "detail",   ""),
        ("Value per share",           ["$121.88"],                                             "total",    ""),
    ]) }}
```

Rules: state the terminal value as a PERCENTAGE of enterprise value — above
about 70% the exercise is a terminal-value estimate wearing a forecast, and the
reader must be told. Every assumption that moves the answer lives in
`assumptions`, including the valuation date. Net debt is added or subtracted
explicitly with its own line and note; a silent enterprise-to-equity step is
where most errors hide. Always pair with `sensitivity_table` — a single DCF
number published without its grid is false precision. If the output is far from
the market price, the interesting question is what the market is assuming, and
that belongs in the text below.
