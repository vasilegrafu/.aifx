# return-distribution

_Authoring guidance for the `return-distribution` component — when to use it, how, and the rules._

A box plot: the **spread** of an outcome rather than its average. Monthly return
dispersion across strategies, analyst estimate ranges, holding-period outcomes.
Rendered by [[apache-echarts]] through the shared frame.

**Use when** the average is the least interesting thing about the data. Two
funds with the same mean return and different dispersion are not the same
investment, and a bar chart of means cannot say so.

## Markup

Pass the **raw observations**. The macro derives the quartiles.

```html
{% raw %}{{ c.return_distribution(
     series=[("Strategy A", [2.1, -0.4, 3.3, 1.8, -1.2, 4.0, 0.9]),
             ("Strategy B", [0.8, 1.1, 0.9, 1.0, 1.2, -8.4, 1.1])],
     caption="Monthly returns, 2023-2025",
     unit="% per month",
     note="B looks steadier on average and carries the only tail that matters.") }}{% endraw %}
```

- `series` — `(label, [values])`. Raw numbers, not summaries.
- `unit` (default `"%"`) — the y-axis name.
- `height` (default `340`), `note`, `caption` as elsewhere.

## What is computed, and how

At compose time, so the rendered spec carries the derived numbers and a reader
can check them against your source:

- **Quartiles** by linear interpolation between order statistics — the default
  of R's `quantile` type 7 and numpy's `percentile`.
- **Whiskers** are Tukey's: the furthest observation still within 1.5 × IQR of
  the box. **Not** the extremes.
- **Outliers** beyond those fences are drawn separately, as points in the
  negative tone.

That last split is the reason this is a component. An outlier quietly extending
a whisker is how a fat tail disappears from a chart — the box looks a little
wider and nobody sees the −8.4. Drawn as a point, it is unmissable.

## Rules

- **Raw values in.** Passing pre-computed quartiles produces a chart that is
  wrong in a way nothing will flag.
- **State n.** A box plot over seven observations and one over seven hundred
  look identical and mean very different things. Put the sample size in
  `caption` or `note`.
- **Comparable periods only.** Two series measured over different windows do
  not belong in one figure; the reader will compare them anyway.
- **The outliers are usually the point.** If the note does not mention them, ask
  why you drew a distribution instead of a mean.
- Fewer than ~5 observations per series: use a table. There is no distribution
  to show.
