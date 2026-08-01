# waterfall

_Authoring guidance for the `waterfall` component — when to use it, how, and the rules._

How a total became another total — a bridge of additive steps. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** you are explaining a CHANGE rather than a level — last year's revenue to this year's, budget to actual, EBITDA to free cash flow.

## Markup

```html
{% raw %}{{ c.waterfall(steps=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `steps, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **The steps must reconcile.** Start plus every delta must equal the end.
  Nothing in the rendering checks this, and a waterfall that does not tie is a
  chart that lies.
- `kind` is `start`, `delta` or `total`. Deltas float; starts and totals sit on
  the axis.
- Bars are coloured by direction, not identity — see [[bar-negative]].
- **Consider [[bridge]] instead.** It is the same decomposition as a table with
  bars: no engine, no CDN, prints perfectly, and the numbers are selectable
  text. Reach for this chart version when the magnitudes need a shared axis,
  and for `bridge` when the figures need to be read.
