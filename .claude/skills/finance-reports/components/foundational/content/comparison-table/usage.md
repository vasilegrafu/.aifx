# comparison-table

_Authoring guidance for the `comparison-table` component — when to use it, how, and the rules._

Styled by: `css/foundational/content.css`

A feature/option matrix: first column = criteria, remaining columns = the
options; cell values `"yes"`, `"no"`, `"part"` render as colored ✓ / ✗ / ◐
marks, anything else as text.

## Markup

```jinja
{{ c.comparison_table(
    headers=["", "PostgreSQL", "SQLite"],
    rows=[
      ["Concurrent writers", "yes", "no"],
      ["Zero administration", "part", "yes"],
      ["Max size", "unlimited", "281 TB"],
    ]) }}
```

## Rules

- **Phrase every criterion so that "yes" is the desirable answer.** A column of
  ✓ and ✗ is read as a score, so a criterion where "no" is better inverts the
  whole picture silently.
- **The table itself stays neutral.** A verdict row, or a decision callout
  following it, draws the conclusion — the marks present evidence and stop
  there.
- **`part` is for a genuine partial, not for a hedge.** If the answer needs a
  sentence, put the sentence in the cell as text; that is why anything else
  renders as prose.
