# stacked-line

_Authoring guidance for the `stacked-line` component — when to use it, how, and the rules._

Several series summed at each point, drawn as lines — the total and its parts. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** you want the running total AND the parts, and the parts are genuinely additive.

## Markup

```html
{% raw %}{{ c.stacked_line(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Only stack things that sum to something real.** Stacked percentages, stacked
  averages and stacked rates are all meaningless.
- **Only the bottom series can be read off the axis.** Every series above it is
  measured from a moving baseline, which is why a reader can compare the
  bottom band over time and no other.
- Prefer [[stacked-area]] — with lines the stacking is easy to miss entirely.
