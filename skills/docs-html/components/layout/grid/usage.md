# grid

_Authoring guidance for the `grid` component — when to use it, how, and the rules._

Styled by: `css/layout.css`

An auto-fit grid of **equal** tiles: it fits as many columns as the width allows,
then wraps — no column count to declare. Ideal for a row of [[card]]s, small
[[figure]]s, or feature tiles. Reflows to fewer columns as the page narrows and
to one in print.

## Markup

```html
{% raw %}{% call c.grid() %}
  {% call c.card("Throughput") %}{{ c.kpi_tiles(...) }}{% endcall %}
  {% call c.card("Latency") %}…{% endcall %}
  {% call c.card("Errors") %}…{% endcall %}
{% endcall %}{% endraw %}
```

- `min` (default `"14rem"`) — the smallest a tile may get before the grid drops a
  column. Raise it for wider content, lower it for denser tiles.

## Rules

- Tiles are **equal** by design. For a deliberate asymmetric split use [[columns]]
  with `span`.
- Give tiles similar-length content so rows stay tidy; a [[card]] per tile is the
  usual choice.
- It's a layout, not data: a grid of numbers is still [[kpi-tiles]]; a grid of
  chart tiles is small-multiples, each a [[chart-echarts]].
