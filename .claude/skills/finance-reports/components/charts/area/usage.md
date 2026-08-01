# area

_Authoring guidance for the `area` component — when to use it, how, and the rules._

A measure over time with the region beneath filled — magnitude, not just direction. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** the quantity under the line means something — cumulative flow, a level that accumulates. The fill says *volume*, so only use it where volume is real.

## Markup

```html
{% raw %}{{ c.area(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **The fill implies the area has meaning.** For a ratio, a rate or a price, it
  does not — use [[line]].
- **Baseline at zero.** A filled area on a truncated axis is actively
  misleading: the fill is sized by the axis, not by the data.
- One or two series only. Overlapping translucent fills stop being readable fast
  — beyond two, use [[stacked-area]].
