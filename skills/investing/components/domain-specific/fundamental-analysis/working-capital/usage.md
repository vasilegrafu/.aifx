# working-capital

_Authoring guidance for the `working-capital` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Days sales outstanding, days inventory, days payable, and the cash conversion
cycle they produce. A negative cycle means suppliers fund the business, which is
a structural advantage worth more than a point of margin; a deteriorating cycle
is the earliest visible sign that reported earnings are running ahead of cash.

```jinja
{{ c.working_capital(
    caption="Working capital efficiency (days)",
    periods=["FY2023", "FY2024", "FY2025"],
    note="Cash conversion cycle = DSO + DIO − DPO. A negative cycle means suppliers fund working capital; it has widened by 10 days over three years.",
    rows=[
        ("Days sales outstanding (DSO)",    ["28.1", "31.2", "31.5"], "",      "up"),
        ("Days inventory outstanding (DIO)", ["6.0",  "9.0",  "9.6"],  "",      "up"),
        ("Days payable outstanding (DPO)",  ["106.7", "119.6", "120.3"], "",   "up"),
        ("Cash conversion cycle",           ["(72.6)", "(79.4)", "(79.2)"], "total", "down"),
    ]) }}
```

Rules: state the formula in `note` — there are several conventions for each
ratio and the reader cannot check you without knowing which one you used. Say
whether the denominators are period-end or average balances; period-end
overstates efficiency for a company whose sales are seasonal. `dir` describes
the METRIC, not whether it is good news: rising DPO is `up` and is usually
favourable, and the interpretation belongs in `note`. Three periods minimum —
one year of working capital tells you about the quarter it ended in, not the
business. Where a change comes from a one-off (a supplier finance programme, a
factoring facility), that is the finding and it must be named.
