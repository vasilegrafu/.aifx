# funnel

_Authoring guidance for the `funnel` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

Magnitudes narrowing from a wide top to a specific bottom. Two canonical uses:
market sizing (total addressable market down to what this company can realistically
serve) and conversion (visitors down to paying customers). The value of the
form is that each step forces you to state a rate and defend it.

```jinja
{{ c.funnel(
    caption="Market sizing — enterprise workflow software",
    note="The SOM implies 3.1% share of the serviceable market by FY2030, against 1.2% today. That share gain is the entire growth case.",
    stages=[
        ("Total addressable market", "$84B",  100, "All enterprise workflow spend, global."),
        ("Served by cloud vendors",  "$51B",   61, "Excludes on-premise and bespoke build (39%)."),
        ("Mid-market and above",     "$34B",   40, "Below 500 seats is served by self-serve tools at a tenth of the price."),
        ("English-speaking regions", "$21B",   25, "Product is not localised; localisation is a FY2028 roadmap item."),
        ("Realistic 5-year share",   "$650M",   8, "3.1% of the serviceable market."),
    ]) }}
```

Bar widths come from a `data-pct` attribute read by CSS `attr()` in
Chromium/Edge and applied by `attr-fallback.js` everywhere else; every stage
also prints its value.

Rules: each stage states WHY it is smaller than the one above — an unexplained
narrowing is where market sizing turns into wishful arithmetic. Widths are
relative to the first stage, so the final bar stays visible even when tiny
(a floor keeps it legible); if the last stage is under about 3% of the top, say
the ratio in `note` because the picture cannot show it honestly. Four to six
stages. Never present a top-down TAM without also stating the implied share, as
above — the share number is the claim, and the TAM is just context.
