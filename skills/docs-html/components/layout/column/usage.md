# column

_Authoring guidance for the `column` component — when to use it, how, and the rules._

Styled by: `css/layout.css`

One cell inside a [[columns]] row. Holds any components; they flow top-to-bottom
inside the cell with the normal `--block-gap` rhythm (first/last margins trimmed).

## Markup

```html
{% raw %}{% call c.column() %}
  {{ c.section(...) }}
  {% call c.callout("warning") %}…{% endcall %}
{% endcall %}{% endraw %}
```

- `span` (default `1`) — relative width. `span=2` next to a `span=1` cell makes a
  2 : 1 split. Omit for equal columns.

## Rules

- **Only inside [[columns]].** A bare `column` does nothing on its own.
- Keep a cell's content self-contained — it may end up full-width when the row
  stacks.
- Don't set widths in px; use `span` so the row stays fluid.
