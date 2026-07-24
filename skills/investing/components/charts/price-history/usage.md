# price-history

_Authoring guidance for the `price-history` component — when to use it, how, and the rules._

Candlestick price action with volume in a second panel beneath, sharing one
time axis. Rendered by [[apache-echarts]] through the shared frame.

**Use when** the *path* matters — gaps, ranges, where volume confirmed a move.
If only the closing level matters, a plain `line` recipe is honest and lighter;
a candlestick that nobody reads the wicks of is four times the ink for the same
information.

## Markup

```html
{% raw %}{{ c.price_history(
     bars=[("2025-01", 185.2, 191.4, 183.0, 193.1, 421_000_000),
           ("2025-02", 191.4, 188.7, 186.2, 195.8, 388_000_000),
           ("2025-03", 188.7, 201.3, 187.9, 202.6, 512_000_000)],
     caption="Share price and volume, FY2025",
     note="March volume confirmed the breakout; February did not.") }}{% endraw %}
```

- `bars` — `(date, open, close, low, high, volume)`. Note the order: it is
  OHLCV as a human reads it. The macro reorders to ECharts' internal
  `[open, close, low, high]` for you.
- `height` (default `420`) — the two panels split it roughly 56% / 16%.

## Why this is a macro and not a recipe

Two panels, not two axes. Price and volume have unrelated scales, and the
tempting way to draw them — one grid, a second y-axis on the right — is exactly
the dual-axis mistake the charting rules forbid, because it lets you imply any
correlation you like by choosing the scales. Two stacked grids with a linked
axis pointer show the same relationship without inventing one.

Getting that right by hand is ~40 lines of `grid` / `xAxisIndex` / `yAxisIndex`
bookkeeping, and getting it wrong looks fine. The macro makes the correct form
the easy one.

## Direction is not identity

Up bars render **hollow** with a positive-tone border; down bars render
**filled** in the negative tone. The fill, not the colour, is the primary
signal — which is deliberate, because the positive and negative tones are the
one pair that collapses under deuteranopia. A reader who cannot distinguish red
from green still reads hollow versus solid.

This is the documented exception to *status colours are reserved*: up and down
encode direction, not series membership.

## Rules

- **One instrument per chart.** Two candlestick series in one panel is
  unreadable; use small multiples, or index both to a common base and use a
  `line`.
- **Volume is context, not a second argument.** It is deliberately muted and
  short. If volume is the point, chart it on its own.
- **Say what the path shows** in `note`. "The stock went up" is visible; "the
  breakout held on rising volume" is the analysis.
- Long histories belong in a `line`. Candlesticks stop being legible somewhere
  around 60 bars — past that the wicks are noise.
