# risk-matrix

_Authoring guidance for the `risk-matrix` component — when to use it, how, and the rules._

Styled by: `css/modules/blocks.css`

The classic 5×5 probability × impact heat grid: rows = probability (5 top),
columns = impact, cells banded green/amber/red by score (≤4 low, ≤12 medium,
>12 high). Risks are placed as id chips; hover shows the label.

```jinja
{{ c.risk_matrix([
    ("RISK-01", 4, 5, "Broker session drops during trading hours"),
    ("RISK-02", 2, 3, "CDN outage degrades rendered documents"),
]) }}
```

Rules: ids match the risk-register entries (trace-ids); scores are the
REGISTER's scores, the matrix only visualizes; more than ~12 chips → the
matrix stops communicating, split by category.
