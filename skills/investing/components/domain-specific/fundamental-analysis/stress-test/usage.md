# stress-test

_Authoring guidance for the `stress-test` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Named stresses, what triggers each one, what it does to the portfolio, and what
you would actually do about it. The response column is what separates a stress
test from a worry list: a scenario with no pre-agreed response is a scenario you
will improvise through at the worst possible moment.

```jinja
{{ c.stress_test(
    caption="Portfolio stress scenarios — impact on NAV",
    note="Magnitudes are scaled to the worst case (-38%). Correlations are assumed to rise toward 1 in every stress, which is the historical pattern and makes these estimates optimistic if anything.",
    rows=[
        ("2008-style credit event", "Spreads above 800bp, funding freeze",
         "-38%", 100, "bad", "Hold; cash reserve funds 18 months of drawdowns without forced selling."),
        ("Rate shock +200bp",       "Ten-year yield above 6%",
         "-22%", 58, "bad", "Trim duration-sensitive names; add to cash-generative positions."),
        ("Technology de-rating",    "Sector multiple back to 20-year median",
         "-28%", 74, "bad", "Thesis-driven; reduce only where the multiple was the thesis."),
        ("Sustained inflation 5%+", "Core PCE above 5% for two quarters",
         "-11%", 29, "warn", "Rotate toward pricing power; no forced action."),
        ("Single-name fraud",       "Accounting restatement at the largest holding",
         "-18%", 47, "bad", "Position cap of 20% is the control; exit on restatement."),
    ]) }}
```

Rules: every scenario has a named, observable TRIGGER — "a market crash" is not
a scenario, "spreads above 800bp" is. The response is a decision you commit to
now, and if the honest response is "hold and do nothing", write that: it is a
real answer and a better one than a plan you will not follow. Magnitudes are
scaled to the worst case so the bars compare. State your correlation assumption
in `note` — most stress tests fail because diversification disappears exactly
when it is needed. Include at least one idiosyncratic scenario alongside the
macro ones; concentration risk kills more portfolios than recessions.
