# meter

_Authoring guidance for the `meter` component — when to use it, how, and the rules._

Styled by: `css/foundational/blocks.css`

A value-vs-target progress bar: label left, value right, a filled track below.
For allocation against bands, goals, utilization, completion.

## Markup

```jinja
{{ c.meter(label="Equities vs 60% target", value=54, max=60, display="54%") }}
```

The fill width comes from a `data-pct` attribute (the authoring contract
forbids `style=`), consumed by CSS `attr()` in Chromium/Edge and applied by
`attr-fallback.js` everywhere else, so the fill is proportional in every
browser.

## Rules

- **`display` carries the human-formatted value**, and it is what the reader
  actually reads. `value` and `max` only drive the geometry, so the two can
  disagree — which is the point when the formatted figure needs a unit, a
  currency or a rounding the raw number does not carry.
- **A meter over 100% clamps visually.** The track cannot show overflow, so
  say so in `display` — an over-target position that renders as "full" is the
  one reading this component gets silently wrong.
- **`max` is the target, not the scale maximum.** A 54-of-60 meter is 90% of
  its target, not 54% of anything; choosing `max=100` out of habit throws the
  comparison the component exists to make.
- One quantity against one reference. A meter is not a chart — for several
  series or a distribution, use a bar chart, which can carry an axis.
