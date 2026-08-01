# stacked-horizontal-bar

_Authoring guidance for the `stacked-horizontal-bar` component — when to use it, how, and the rules._

Parts summing to a whole, laid on their side — for long category names. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** the category labels are long, or there are many of them. Horizontal bars give labels a full line of room and read top to bottom like a list.

## Markup

```html
{% raw %}{{ c.stacked_horizontal_bar(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- Categories read **top to bottom in the order given** — the axis is inverted
  for you, so pass them already sorted.
- **Only stack additive quantities**, and only the leftmost segment shares a
  baseline.
- Zero-based axis, as with every bar.
