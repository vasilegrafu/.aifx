# pie

_Authoring guidance for the `pie` component — when to use it, how, and the rules._

Composition of a single whole — a donut, for a handful of parts. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** there are **three or four parts** of one whole and the split is roughly the only thing being said.

## Markup

```html
{% raw %}{{ c.pie(slices=…, caption=…, donut=…) }}{% endraw %}
```

Parameters: `slices, caption, height, note, donut`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Past four slices, use [[bar]] or [[stacked-normalized]].** Angle is the
  least accurately read encoding there is; a bar chart of the same data is
  strictly easier to read and nobody has ever missed the pie.
- **Slices must sum to a meaningful whole.** If there is an "Other", show it.
- Never two pies side by side for a before/after — that comparison is a
  [[stacked-normalized]] with two columns.
- A donut by default: the hole removes the temptation to read total area.
