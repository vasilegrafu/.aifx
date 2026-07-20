# comparison-table

_Authoring guidance for the `comparison-table` component — when to use it, how, and the rules._

Styled by: `css/modules/content.css`

A feature/option matrix: first column = criteria, remaining columns = the
options; cell values `"yes"`, `"no"`, `"part"` render as colored ✓ / ✗ / ◐
marks, anything else as text.

```jinja
{{ c.comparison_table(
    headers=["", "PostgreSQL", "SQLite"],
    rows=[
      ["Concurrent writers", "yes", "no"],
      ["Zero administration", "part", "yes"],
      ["Max size", "unlimited", "281 TB"],
    ]) }}
```

Rules: criteria phrased so "yes" is desirable; a verdict row or following
decision callout draws the conclusion — the table itself stays neutral.
