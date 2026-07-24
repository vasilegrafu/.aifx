# line

_Authoring guidance for the `line` component — when to use it, how, and the rules._

A measure over time — the default form for anything with a date axis. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** the x axis is time and the reading is direction. It is the most honest default in the catalogue: position encodes value, nothing is stacked, and nothing is hidden behind anything else.

## Markup

```html
{% raw %}{{ c.line(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Time on x, always left to right.** A line chart of unordered categories is a
  bar chart badly drawn — the slope between two categories means nothing.
- **Do not truncate the y axis to exaggerate a move.** If you need a zero-free
  axis, say so in `note`.
- Past ~6 series the lines cross into noise; facet instead.
