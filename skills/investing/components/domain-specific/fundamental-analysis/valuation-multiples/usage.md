# valuation-multiples

_Authoring guidance for the `valuation-multiples` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Every multiple judged twice: against what peers trade at, and against what
this company itself has traded at. The premium column is the only number most
readers keep. The verdict pill (`cheap` / `fair` / `rich`) reuses the `badge`
component so verdicts look the same everywhere in the document set.

```jinja
{{ c.valuation_multiples(
    caption="Apple vs mega-cap hardware and platform peers",
    rows=[
        ("P/E (NTM)",    "31.2x", "24.8x", "27.4x", "+14% vs own",  "rich"),
        ("EV/EBITDA",    "23.1x", "17.9x", "20.2x", "+14% vs own",  "rich"),
        ("EV/Sales",     "8.4x",  "6.1x",  "7.2x",  "+17% vs own",  "rich"),
        ("FCF yield",    "3.4%",  "4.1%",  "3.8%",  "-0.4pp",       "fair"),
        ("PEG (NTM)",    "2.6x",  "1.9x",  "2.2x",  "+18% vs own",  "rich"),
    ]) }}
```

Rules: state the basis in the caption — trailing, next-twelve-months, or
fiscal year — and use ONE basis for the whole table. Name the peer set in the
caption or a footnote; an unnamed "peer median" is unfalsifiable. A premium is
not a sell and a discount is not a buy: the verdict column is your read, and
the reasoning belongs in `thesis_pillars`. Every multiple in the table must be
one you would actually act on — drop the ones you are only quoting for
completeness. Pair with `valuation_range` when the conclusion is a price, not
a rating.
