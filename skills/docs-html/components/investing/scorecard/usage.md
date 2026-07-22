# scorecard

_Authoring guidance for the `scorecard` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

Scores a candidate against weighted criteria and shows the weighted total —
the component for any judgement that has to be repeatable across names:
moat, business quality, management, capital allocation, ESG, counterparty.
Weights force you to say what matters before you look at the answer.

```jinja
{{ c.scorecard(caption="Moat assessment", scale=5, total="3.9 / 5 — wide", rows=[
    ("Intangible assets", "30%", 5, "Brand carries a 20%+ price premium at like-for-like specification."),
    ("Switching costs",   "25%", 4, "iCloud, iMessage and purchase history; 92% retention on upgrade."),
    ("Network effect",    "15%", 3, "App Store two-sided, but developers multi-home to Android."),
    ("Cost advantage",    "20%", 4, "Silicon in-house; scale purchasing on displays and memory."),
    ("Efficient scale",   "10%", 2, "No structural limit on entrants at the low end."),
]) }}
```

The rating bar width comes from a `data-pct` attribute computed at compose
time (the authoring contract forbids `style=`), consumed by CSS `attr()` in
Chromium/Edge and applied by `attr-fallback.js` everywhere else, so the bar
matches the numeric score in every browser.

Rules: weights sum to 100% and are set BEFORE scoring, not tuned until the
total agrees with a conclusion you already had. Every score carries evidence
in the same row — an unsupported score is `<mark class="todo">`, not a number.
Keep the scale consistent across every document in a project (5 is the
default) so scores compare. The total is stated in the document, not computed
at view time; recompute it by hand when a score changes.

Standard rubrics worth reusing: moat (the five sources above), management
(capital allocation, incentives, candour, succession), business quality
(pricing power, reinvestment runway, cyclicality, balance sheet).
