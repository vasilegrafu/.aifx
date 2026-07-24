# variance-analysis

_Authoring guidance for the `variance-analysis` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Budget against actual, with the variance and an explicit favourable or adverse
verdict. The verdict column exists because the sign of a variance does not tell
you its direction: spending less than budget is favourable on cost and adverse
on a marketing line that was supposed to buy growth.

```jinja
{{ c.variance_analysis(
    caption="Operating budget", period="H1 FY2026", unit="$000",
    note="The revenue shortfall is timing: two enterprise contracts slipped from June to July and closed at full value.",
    rows=[
        ("Revenue",              "12,400", "11,860", "(540)",  "-4.4%",  "adverse"),
        ("Cost of sales",        "(4,960)", "(4,620)", "340",  "-6.9%",  "favourable"),
        ("Gross profit",         "7,440",  "7,240",  "(200)",  "-2.7%",  "adverse"),
        ("Marketing",            "(1,860)", "(1,240)", "620",  "-33.3%", "adverse"),
        ("Engineering",          "(2,480)", "(2,510)", "(30)", "+1.2%",  "neutral"),
        ("General and admin",    "(1,120)", "(1,080)", "40",   "-3.6%",  "favourable"),
    ],
    total_row=("Operating profit", ["1,980", "2,410", "430", "+21.7%", ""])) }}
```

Rules: the verdict is a JUDGEMENT and must sometimes contradict the sign — the
marketing underspend above is adverse because it bought the profit beat by
cutting future revenue, and a table that marked it favourable would be
misleading. Percentages are of budget, not of actual. Every adverse variance
above your materiality threshold gets an explanation in `note` or in the text;
an unexplained variance is an open question, not a finding. Distinguish timing
from permanent differences explicitly. Use the same sign convention as the
underlying statements — costs in parentheses throughout.
