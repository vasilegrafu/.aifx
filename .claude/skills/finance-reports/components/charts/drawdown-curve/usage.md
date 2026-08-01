# drawdown-curve

_Authoring guidance for the `drawdown-curve` component — when to use it, how, and the rules._

Peak-to-trough decline over time: how far below its own high-water mark a
series has been, and for how long. Rendered by [[apache-echarts]] through
the shared frame.

**Use when** the risk is the argument. A rising equity curve hides the
experience of holding it; the drawdown curve is that experience. Pair it with
the price or NAV line rather than replacing it — one shows the return, the
other shows what it cost to sit through.

## Markup

Pass the level series. The macro derives the drawdown.

```html
{% raw %}{{ c.drawdown_curve(
     series=[("2023-01", 100.0), ("2023-06", 118.4), ("2023-09", 96.2),
             ("2024-03", 121.7), ("2024-11", 104.9), ("2025-06", 138.2)],
     caption="Drawdown from running peak, 2023-2025") }}{% endraw %}
```

- `series` — `(date, value)`. Any level series: price, NAV, index, cumulative
  return. **Not** a return series — feed it levels and it computes the rest.
- `height` (default `300`) — a drawdown curve is a supporting panel; it does
  not need the height of a price chart.
- `note` — omit it and the macro writes the maximum drawdown for you. Supply
  one to say something the number does not.

## The arithmetic is done at compose time

The running peak and each drawdown are computed in the macro, so the rendered
JSON contains the derived percentages and the document carries the input series
you gave it. Two consequences worth knowing:

- The numbers are **auditable** — they are in the file, not produced by a script
  at view time. A reader can check them.
- The peak is computed from the series **as supplied**. Start it after the
  actual peak and the first drawdown reads as zero, which flatters the record.
  Begin at a genuine high-water mark, or at inception.

The maximum drawdown is marked on the curve and stated beneath it, because the
single number is what gets quoted and it should not require reading the axis.

## Rules

- **Levels, never returns.** Passing period returns produces a chart that looks
  plausible and means nothing. This is the one way to misuse the component.
- **Zero is the ceiling.** The y-axis is pinned at `max: 0` — drawdown is
  negative by construction. A positive value means the input is not a level
  series.
- **Match the period to the claim.** A drawdown curve starting in 2023 says
  nothing about 2008. If the strategy is untested through a real crisis, say so
  in `note`; the chart cannot.
- **Recovery time is half the story.** Depth is on the axis; duration is the
  width of the trough. If the recovery took three years, write it — the shape
  shows it but the reader may not measure it.
