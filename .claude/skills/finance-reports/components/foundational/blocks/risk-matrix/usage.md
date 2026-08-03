# risk-matrix

_Authoring guidance for the `risk-matrix` component — when to use it, how, and the rules._

Styled by: `css/foundational/blocks.css`

The classic 5×5 probability × impact heat grid: rows = probability (5 top),
columns = impact, cells banded green/amber/red by score (≤4 low, ≤12 medium,
>12 high). Risks are placed as id chips; hover shows the label.

## Markup

```jinja
{{ c.risk_matrix([
    ("RISK-01", 4, 5, "Broker session drops during trading hours"),
    ("RISK-02", 2, 3, "CDN outage degrades rendered documents"),
]) }}
```

## Rules

- **Ids match the risk-register entries** (trace-ids), so a chip on the grid
  and a row in the register are the same risk.
- **Scores are the REGISTER's scores.** The matrix only visualizes — it is
  never the place a score is decided or revised.
- **More than about twelve chips and the matrix stops communicating.** Split by
  category rather than shrinking the labels.
