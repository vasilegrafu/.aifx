# correlation-matrix

_Authoring guidance for the `correlation-matrix` component — when to use it, how, and the rules._

A heatmap of pairwise relationships across a set — asset correlations, factor
loadings, segment co-movement. Rendered by [[apache-echarts]] through the
shared frame.

**Use when** the *pattern* across many pairs is the finding. For three or four
assets a table is better: exact numbers, no colour to decode.

## Markup

```html
{% raw %}{{ c.correlation_matrix(
     labels=["Equities", "Bonds", "Gold", "REITs"],
     matrix=[[1.00,  0.12, -0.08,  0.71],
             [0.12,  1.00,  0.24,  0.19],
             [-0.08, 0.24,  1.00,  0.05],
             [0.71,  0.19,  0.05,  1.00]],
     caption="Monthly return correlation, 2020-2025",
     note="REITs are an equity position wearing a different name.") }}{% endraw %}
```

- `labels` — names, in order.
- `matrix` — `matrix[i][j]` is the value for `labels[i]` against `labels[j]`.
  Written the way you would write it on paper; the macro flips row order so the
  first label lands top-left.
- `vmin` / `vmax` (default `-1` / `1`) — the colour scale bounds. Change them
  for data that is not a correlation.

## Why the ramp and not the palette

A correlation is **ordered** data. The categorical palette would imply unrelated
categories, and ECharts' stock blue-to-red `visualMap` reads as good-to-bad — a
judgement the number does not carry. A −0.8 correlation is not "bad"; for a
diversifier it is the whole point.

So the scale is the design system's sequential `RAMP`, referenced as
`"ramp:1"`…`"ramp:6"` and monotonic in luminance, which is what makes the
matrix survive greyscale printing and every form of colour blindness. Cell
values are printed as well as coloured — colour ranks, text tells you by how
much.

## Rules

- **Symmetric and diagonal-1**, for a true correlation matrix. If yours is not,
  it is not a correlation — relabel the figure honestly.
- **Say the period and the frequency.** Correlations are unstable; a monthly
  correlation over five years and a daily one over five months are different
  claims. Put both in `caption`.
- **Correlation is not causation, and not risk.** Two assets can be uncorrelated
  for years and fall together in the week that matters. If the argument is
  diversification, pair this with a [[stress-test]] or a [[drawdown-curve]].
- Past roughly 12 labels the cells are too small to read; group first.
