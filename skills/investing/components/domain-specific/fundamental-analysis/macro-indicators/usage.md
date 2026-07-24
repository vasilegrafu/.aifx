# macro-indicators

_Authoring guidance for the `macro-indicators` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The macro dashboard: each indicator with its latest print, the prior print,
what was expected, the surprise, and the direction of travel. The opening
block of a market outlook or economic analysis — it establishes the state of
the world before any argument about what to do with it.

```jinja
{{ c.macro_indicators(caption="United States", asof="2026-07-17", rows=[
    ("CPI y/y",                   "2.6%",  "2.8%",  "2.7%",  "-0.1pp", "down"),
    ("Core PCE y/y",              "2.4%",  "2.5%",  "2.4%",  "0.0pp",  "down"),
    ("Unemployment rate",         "4.3%",  "4.2%",  "4.2%",  "+0.1pp", "up"),
    ("Non-farm payrolls (3m avg)", "118k",  "142k",  "135k",  "-17k",   "down"),
    ("ISM manufacturing",         "49.1",  "48.4",  "48.9",  "+0.2",   "up"),
    ("10y Treasury yield",        "4.12%", "4.31%", "—",     "—",      "down"),
    ("Fed funds (upper)",         "4.25%", "4.50%", "4.25%", "0.0",    "down"),
]) }}
```

Rules: one economy per table — a mixed US/EU/China dashboard hides the
divergence that is usually the finding. Every row states its unit and basis in
the indicator name (`y/y`, `3m avg`, `ann.`), never in a footnote. Surprises
are in the indicator's own unit (pp, k, index points). `dir` is the direction
of the SERIES, not whether it is good news — falling payrolls are `down`, and
whether that helps the position is the analyst's job to say underneath. Print
dates matter: an indicator released before the `asof` date is stale and the
caption must say so. Pair with `cycle_position` for the synthesis.
