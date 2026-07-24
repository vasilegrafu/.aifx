# attribution

_Authoring guidance for the `attribution` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Brinson attribution: for each segment, what the portfolio held against what the
benchmark held, what each returned, and how much of the excess came from being
in the right places (allocation) versus owning the right names within them
(selection). It is the only honest answer to "were you right, or just exposed?"

This is a wide table — pair it with the full-width view or a short segment list.

```jinja
{{ c.attribution(
    caption="Brinson attribution vs MSCI World", period="YTD to 30 Jun 2026",
    note="Excess return is 82% selection. The technology overweight contributed 0.4pp; the rest came from stock choice within it.",
    rows=[
        ("Information technology", "42.3%", "24.1%", "+14.2%", "+11.8%", "+0.44pp", "+1.02pp", "+1.46pp"),
        ("Health care",            "12.6%", "11.8%", "+6.1%",  "+8.4%",  "+0.01pp", "-0.29pp", "-0.28pp"),
        ("Financials",              "8.6%", "16.2%", "+11.0%", "+9.2%",  "-0.09pp", "+0.16pp", "+0.07pp"),
        ("Consumer discretionary", "11.0%", "10.9%", "+9.4%",  "+7.7%",  "+0.00pp", "+0.19pp", "+0.19pp"),
        ("Cash",                    "7.2%",  "0.0%", "+2.1%",  "0.0%",   "-0.42pp", "+0.00pp", "-0.42pp"),
    ],
    total_row=("Total", ["100.0%", "100.0%", "+9.6%", "+8.2%", "-0.06pp", "+1.08pp", "+1.40pp"])) }}
```

Rules: allocation plus selection must reconcile to total excess return — if
your model produces an interaction term, give it its own column rather than
folding it silently into selection. Name the benchmark and confirm it is the one
in the investment policy statement, chosen before the period. Cash is a segment
and usually an allocation drag in a rising market; hiding it overstates skill.
Effects are in percentage points, weights are averages over the period, not
period-end. One period per table. A quarter of attribution is noise — the
conclusion belongs to multi-year tables, and saying so in `note` is more
credible than not.
