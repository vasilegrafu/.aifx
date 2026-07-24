# risk-metrics

_Authoring guidance for the `risk-metrics` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The risk and risk-adjusted-return statistics of a strategy or portfolio, each
against the same statistic for the benchmark, with a one-line reading. The
required companion to `performance-table` in any backtest report or portfolio
review — a strategy is only as good as the drawdown you would have had to sit
through.

```jinja
{{ c.risk_metrics(
    caption="Strategy statistics — 2016-01 to 2026-06, monthly, net of 0.1% round-trip",
    benchmark_label="MSCI World",
    rows=[
        ("CAGR",                 "12.1%",  "11.6%", "Half a point ahead, before considering risk."),
        ("Volatility (ann.)",    "17.8%",  "14.9%", "Concentration costs 2.9pp of volatility."),
        ("Sharpe ratio",         "0.58",   "0.66",  "Below benchmark — the excess return is not paid for."),
        ("Sortino ratio",        "0.91",   "0.98",  "Downside deviation confirms the Sharpe reading."),
        ("Max drawdown",         "-38.4%", "-25.7%", "Peak Feb 2020, trough Mar 2020, recovered Aug 2020."),
        ("Beta",                 "1.14",   "1.00",  "Most of the excess return is leverage to the index."),
        ("Hit rate (monthly)",   "58%",    "—",     "73 of 126 months positive."),
    ]) }}
```

Rules: the caption states the sample window, the data frequency, and the cost
assumption — a backtest without all three is marketing. Every ratio names its
risk-free assumption in a footnote. Max drawdown states peak, trough and
recovery dates, not just the number. The reading column is a sentence about
what the number MEANS for the decision, and an unfavourable reading is stated
plainly — that is the value of the component. Use the same metric set across
every strategy in a project so they compare.
