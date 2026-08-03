# badge

_Authoring guidance for the `badge` component — when to use it, how, and the rules._

Styled by: `css/foundational/blocks.css`

A generic inline status/rating pill: Buy/Hold/Sell, Pass/Fail, risk ratings,
lifecycle states — any short verdict, in any domain.

## Markup

```jinja
{{ c.badge("Buy", "good") }}
```

Variants: `good` (green), `warn` (amber), `bad` (red), `info` (accent), or omit
for neutral gray.

## Rules

- **One or two words, a verdict not a sentence.** A badge holding a clause is a
  table cell that lost its table.
- **Use it inside headings, table cells, or prose** — it is inline, and it does
  not own a line of its own.
- **The variant carries the verdict, so keep the mapping constant** across a
  document set. A `good` that means "buy" in one exhibit and "no action" in the
  next teaches the reader to ignore the colour.
- **For requirement priorities, keep the requirement card's own pills** rather
  than substituting a badge.
