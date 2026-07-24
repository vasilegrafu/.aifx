# dupont

_Authoring guidance for the `dupont` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Return on equity broken into the drivers that multiply to produce it, tracked
across periods. Two companies at 25% ROE are not the same company: one earns it
on margin, the other on leverage, and only the decomposition tells you which
return survives a downturn.

```jinja
{{ c.dupont(
    caption="Return on equity decomposition",
    periods=["FY2023", "FY2024", "FY2025"],
    note="ROE is flattered by a shrinking equity base: buybacks pushed the equity multiplier from 5.7x to 6.4x while margin did the real work.",
    factors=[
        ("Net margin",              ["25.3%", "24.0%", "26.8%"]),
        ("Asset turnover",          ["1.09x", "1.07x", "1.10x"]),
        ("Equity multiplier",       ["5.67x", "6.41x", "5.29x"]),
    ],
    result=("Return on equity", ["156.4%", "164.6%", "156.0%"])) }}
```

Rules: the factors must actually multiply to the result in every column — check
each column, and if rounding makes it miss, say so rather than adjusting a
factor. Use the three-step decomposition (margin × turnover × leverage) unless
the five-step version earns its complexity, and never mix the two in one
document. Where equity is small or negative from buybacks, ROE stops being
meaningful — use return on invested capital instead and say why in `note`. The
`note` is the interpretation: which factor moved, and whether that is quality or
financial engineering. Same periods as the statements in the same document.
