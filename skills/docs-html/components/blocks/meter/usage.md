# meter

_Authoring guidance for the `meter` component — when to use it, how, and the rules._

Styled by: `css/modules/blocks.css`

A value-vs-target progress bar: label left, value right, a filled track
below. For allocation vs bands, goals, utilization, completion.

`{{ c.meter(label="Equities vs 60% target", value=54, max=60, display="54%") }}`

The fill width comes from a `data-pct` attribute (the authoring contract
forbids `style=`), consumed by CSS `attr()` in Chromium/Edge and applied by
`attr-fallback.js` everywhere else, so the fill is proportional in every
browser. Rules: `display` carries the human-formatted value; a meter over 100%
clamps visually — say so in `display`.
