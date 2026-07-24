# thesis-pillars

_Authoring guidance for the `thesis-pillars` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The three to five arguments the position actually rests on. Each pillar states
a claim, the evidence behind it, and the observation that would prove it wrong.
The falsifier is the point of the component: it converts an opinion into
something the next review can check, and it is what you monitor between
reviews.

```jinja
{{ c.thesis_pillars([
    ("Services compounds at 12%+ through FY2028",
     "Services grew 13.1% in FY2025 to $109.2B on a 74% gross margin; installed base up 7% y/y.",
     "Two consecutive quarters of Services growth below 8%, or an adverse App Store ruling in the EU."),
    ("Gross margin re-rates the whole business",
     "Mix shift lifted group gross margin from 43.3% to 46.9% over three years.",
     "Group gross margin falls below 44% for two quarters."),
    ("Buybacks shrink the share count 3% a year",
     "$95B repurchased in FY2025 against a $3.4T cap; net cash still $50B+.",
     "Net buyback drops below $60B a year, or net cash turns negative."),
]) }}
```

Rules: 3–5 pillars — fewer is a hunch, more is a list of everything you know.
Every pillar carries a falsifier, and the falsifier must be observable
(a number, a date, a ruling), never a mood. Evidence cites real figures with
their period. If a pillar's falsifier triggers, the document is updated and the
`recommendation` is revisited in the same edit — that is the whole point of
writing it down.
