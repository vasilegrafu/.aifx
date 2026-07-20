# badge

_Authoring guidance for the `badge` component — when to use it, how, and the rules._

Styled by: `css/modules/business.css`

A generic inline status/rating pill: Buy/Hold/Sell, Pass/Fail, risk ratings,
lifecycle states — any short verdict, in any domain.

`{{ c.badge("Buy", "good") }}` — variants: `good` (green), `warn` (amber),
`bad` (red), `info` (accent), or omit for neutral gray.

Rules: one or two words, a verdict not a sentence; use inside headings, table
cells, or prose. For requirement priorities keep the requirement card's own
pills.
