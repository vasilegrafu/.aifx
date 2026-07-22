# valuation-range

_Authoring guidance for the `valuation-range` component — when to use it, how, and the rules._

Styled by: `css/modules/investing.css`

The football field: one horizontal bar per valuation method, all on a shared
price axis, with today's price marked straight through them. It answers the
only question a valuation section has to answer — is the price inside or
outside what the methods support, and by how much.

```jinja
{{ c.valuation_range(
    caption="Apple — value per share by method", unit="$",
    scale_min=160, scale_max=320, price=232, price_label="Spot $232",
    rows=[
        ("DCF — WACC 8.5%, TGR 3.0%", 214, 286, "$214 – $286"),
        ("Peer P/E 24–30x NTM",       198, 248, "$198 – $248"),
        ("EV/EBITDA 18–23x",          186, 238, "$186 – $238"),
        ("Sum of the parts",          226, 298, "$226 – $298"),
        ("52-week range",             169, 260, "$169 – $260"),
    ]) }}
```

Bar offset and width are computed at compose time and carried as `data-lo` /
`data-span` attributes (the contract forbids `style=`), consumed by CSS
`attr()` in Chromium/Edge and applied by `attr-fallback.js` everywhere else.
The numeric label on every row is never optional — a reader should be able to
check the picture against the number.

Rules: `scale_min` / `scale_max` bound every bar — a range that falls outside
them is clipped silently, so set the axis last, after the ranges are known.
Each method names its key assumption in the label ("WACC 8.5%, TGR 3.0%"), not
just its name. Four to six methods; a field of ten bars says you have no view.
Include the 52-week range as the reality check. The price marker is spot at the
`asof` date in `security_header` — keep the two dates identical.
