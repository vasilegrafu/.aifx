# bullets

_Authoring guidance for the `bullets` component — when to use it, how, and the rules._

An unordered list. Use for points that are genuinely parallel and genuinely
unordered — findings that stand on their own, factors that all bear on one
question.

## Markup

```jinja
{{ c.bullets(items=[
    "Revenue grew on volume, not price.",
    "Gross margin held despite the mix shift.",
    "Free cash flow covered the buyback without new debt.",
]) }}
```

## Rules

- **Unordered means unordered.** If the sequence carries meaning — ranked
  findings, an argument built step on step — use [[numbered]]. A bulleted list
  the reader is meant to read in order is a numbered list that lost its
  numbers.
- **A procedure is not a list of points.** Use [[steps]]; for pass/fail state
  use [[checklist]]. Both carry affordances a reader acting on them needs, and
  bullets carry none.
- **Keep items parallel in grammar and in weight.** A list mixing one clause
  with one paragraph reads as one important item and some filler, which is a
  claim about emphasis nobody meant to make.
- Three to seven items. Past that the list has become a table with one column,
  and the reader has lost the thread by the bottom.
