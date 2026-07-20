# strategy-specification

_Authoring guidance for the `strategy-specification` document type — audience, depth, and rules._

- Audience: the implementer (often atlas code) and the backtest that will
  judge it — the SRS of a trading strategy.
- Filename: `docs/strategy-specification-<name>.html`.
- Depth: full.
- Rules: every rule is COMPUTABLE from the declared data — "when momentum is
  strong" is not a rule; STR- ids trace into the backtest-report; evaluation
  thresholds are declared BEFORE the backtest (else the backtest becomes
  curve-fitting with extra steps); changes = version bump, and prior backtests
  no longer apply.
