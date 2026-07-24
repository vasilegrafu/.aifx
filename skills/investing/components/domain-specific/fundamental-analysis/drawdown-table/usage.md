# drawdown-table

_Authoring guidance for the `drawdown-table` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The worst drawdowns a strategy actually delivered, each with the date it peaked,
the date it bottomed, the date it got back to even, and how long each leg took.
A maximum drawdown quoted as a single number hides the only question that
matters to someone who has to live through it: how long was I underwater?

```jinja
{{ c.drawdown_table(
    caption="Five deepest drawdowns, 2016-01 to 2026-06",
    note="Median time to recovery is 9 months; the 2022 drawdown took 19. Position sizing assumes the ability to hold through a 40% decline lasting two years.",
    rows=[
        ("-38.4%", "2020-02-19", "2020-03-23", "2020-08-18", "1 month",   "5 months",  "Covid liquidity shock"),
        ("-31.2%", "2022-01-03", "2022-10-12", "2024-01-19", "9 months",  "15 months", "Rate shock, multiple compression"),
        ("-19.8%", "2018-10-01", "2018-12-24", "2019-04-23", "3 months",  "4 months",  "Trade war, hawkish Fed"),
        ("-14.1%", "2025-02-19", "2025-04-08", "2025-07-30", "2 months",  "4 months",  "Tariff announcement"),
        ("-11.6%", "2023-07-31", "2023-10-27", "2023-12-08", "3 months",  "1 month",   "Duration sell-off"),
    ]) }}
```

Rules: recovery date, not just depth — a 30% drawdown recovered in four months
and one recovered in three years are different products. Use the same return
series and frequency as `performance_table`; drawdowns computed on monthly data
understate the intraday pain and you should say which you used. Name a cause per
drawdown: an unattributed drawdown teaches nothing about when the next one
comes. An ongoing drawdown shows "not recovered" in the recovery column rather
than being omitted. State in `note` what the table implies for position sizing,
which is the reason a reader is looking at it.
