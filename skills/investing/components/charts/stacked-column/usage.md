# stacked-column

_Authoring guidance for the `stacked-column` component — when to use it, how, and the rules._

Parts summing to a whole across categories — vertical stacked bars. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** each category divides into parts and both the total and the split matter.

## Markup

```html
{% raw %}{{ c.stacked_column(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Only stack additive quantities.**
- **Only the bottom segment shares a baseline**, so only it can be compared
  across categories by eye. Order segments so the one that matters is at the
  bottom.
- For shares rather than totals use [[stacked-normalized]]; for many categories
  or long labels use [[stacked-horizontal-bar]].
