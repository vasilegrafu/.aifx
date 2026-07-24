# trade-log

_Authoring guidance for the `trade-log` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Executed trades with the reasoning attached to each one, written at the time
of the trade. The rationale row is the component's reason to exist: a log of
fills is a broker statement, while a log of fills plus the reason you gave
before the outcome was known is the only honest record of process.

```jinja
{{ c.trade_log(caption="Trades — Q2 2026", rows=[
    ("2026-04-14", "AAPL", "Buy", "250 sh", "$218.40", "open",
     "Added on the DMA headline drawdown; pillar 1 unaffected, Services growth still 12%+. Sized to take weight from 16% to 18.4%."),
    ("2026-05-02", "NVDA", "Sell", "180 sh", "$1,142.00", "+64.2%",
     "Trimmed on valuation, not on thesis: EV/Sales above 22x left no margin of safety. Retained half the position."),
    ("2026-06-11", "XLU", "Buy", "1,200 sh", "$78.10", "-3.1%",
     "Defensive ballast ahead of the rate decision. Mistake in hindsight — this was market timing, not an allocation decision."),
]) }}
```

Rules: the rationale is written BEFORE the outcome is known and never edited
afterwards — corrections go in a later row, not over an earlier one. Say what
the trade did to portfolio weight, not just the share count. Name the trigger
and the pillar it serves, so a review can tell process from luck. Record the
mistakes with the same detail as the wins; a journal with no bad trades in it
is not being kept honestly. Open positions show `open` rather than an
unrealised number that changes daily.
