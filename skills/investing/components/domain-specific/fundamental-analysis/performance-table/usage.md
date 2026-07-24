# performance-table

_Authoring guidance for the `performance-table` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Returns by period for the portfolio, the benchmark it is measured against, and
the excess between them. Three-row minimum: without the benchmark row a return
number means nothing, and without the excess row the reader has to subtract.
Negative cells are tinted automatically from the leading minus sign.

```jinja
{{ c.performance_table(
    caption="Total return, net of costs, to 30 Jun 2026",
    periods=["1M", "3M", "YTD", "1Y", "3Y p.a.", "5Y p.a.", "Since inception p.a."],
    rows=[
        ("Portfolio",       ["+2.1%", "+6.4%", "+9.6%", "+22.4%", "+14.8%", "+12.1%", "+11.4%"], ""),
        ("MSCI World (net)", ["+1.8%", "+5.1%", "+8.2%", "+18.9%", "+13.2%", "+11.6%", "+10.2%"], "benchmark"),
        ("Excess",          ["+0.3pp", "+1.3pp", "+1.4pp", "+3.5pp", "+1.6pp", "+0.5pp", "+1.2pp"], "excess"),
    ]) }}
```

Rules: state net-or-gross and the currency in the caption — the two most
common ways a performance table misleads. Periods over one year are annualised
and labelled `p.a.`; never show a cumulative three-year number beside annual
ones. Excess is in percentage points (pp), not percent. The benchmark is the
one named in the investment policy statement, chosen before the period, not
after. Pair with `risk_metrics` — return without volatility is half the story.
