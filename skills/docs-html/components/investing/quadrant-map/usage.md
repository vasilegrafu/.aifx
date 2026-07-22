# quadrant-map

_Authoring guidance for the `quadrant-map` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

A 2×2 with items placed by two scores: growth against profitability, quality
against valuation, share against growth. The oldest strategy graphic there is,
and still the fastest way to show that a set of candidates separates into
groups — provided both axes are defined, which is where most 2×2s fail.

`quadrants` labels the four zones in reading order: top-left, top-right,
bottom-left, bottom-right.

```jinja
{{ c.quadrant_map(
    caption="Watchlist — quality against valuation",
    x_label="Valuation percentile vs own 10-year history →",
    y_label="Business quality score (0–100) →",
    quadrants=["Quality, cheap", "Quality, expensive", "Weak, cheap", "Weak, expensive"],
    note="Quality is the weighted scorecard total; valuation percentile is the current NTM P/E against the company's own ten-year distribution. Top-left is the buy zone; nothing sits there today.",
    items=[
        ("AAPL",  82, 78, "neutral"),
        ("MSFT",  88, 86, "neutral"),
        ("GOOGL", 41, 81, "good"),
        ("META",  55, 68, "good"),
        ("INTC",  36, 24, "bad"),
        ("IBM",   72, 38, "neutral"),
    ]) }}
```

Item positions come from `data-x` / `data-y` attributes computed at compose time
(the contract forbids `style=`), read by CSS `attr()` in Chromium/Edge and
applied by `attr-fallback.js` everywhere else. State the conclusion in `note`
regardless — a scatter of labels is an argument only once someone names it.

Rules: both axes must be DEFINED and measurable, with the definition in `note` —
"quality" and "attractiveness" as bare labels make the chart unfalsifiable.
Scores are 0–100 so placements are comparable across documents. Eight items is
the readable maximum before labels collide. Name the quadrants with what they
MEAN for action, not with cute names. Say which quadrant you are buying from,
and if it is empty, say that too — an empty buy zone is a finding.
