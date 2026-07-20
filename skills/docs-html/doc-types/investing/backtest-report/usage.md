# backtest-report

_Authoring guidance for the `backtest-report` document type — audience, depth, and rules._

- Audience: the strategy's judge — pairs with strategy-specification like a
  test report pairs with an SRS.
- Filename: `docs/backtest-report-<strategy>-<date>.html`.
- Depth: none — written from real runs.
- Rules: names the exact spec version tested; costs are modeled and their
  sensitivity shown (a strategy that dies at 2× costs is dead); out-of-sample
  results reported separately, degradation stated; the variant count
  (how many ideas were tried) is disclosed — it is the overfitting prior;
  verdict strictly against the spec's PRE-declared criteria.
