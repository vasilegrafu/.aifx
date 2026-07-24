# composite-score

_Authoring guidance for the `composite-score` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

A published composite — Altman Z, Piotroski F, Beneish M, Ohlson O — shown with
its formula, every input, each input's contribution, and the band the result
falls in. The contribution column is the point: a Z-score of 2.4 driven by a
collapsing working capital term is a different warning from the same score
driven by a depressed market cap.

The `formula` is rendered as LaTeX by KaTeX at view time (it uses the `math`
class), so write it as TeX source, never as an image.

```jinja
{{ c.composite_score(
    name="Altman Z-score (manufacturing)",
    formula="Z = 1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 1.0X_5",
    caption="Inputs, FY2025",
    score="3.41", band="Safe", tone="good",
    bands=[("Distress", "< 1.81", "bad"), ("Grey", "1.81 – 2.99", "warn"), ("Safe", "> 2.99", "good")],
    note="The score rests on X4 (market value of equity to total liabilities); a 40% de-rating alone would move it into the grey zone.",
    inputs=[
        ("X₁ Working capital / total assets",       "1.2", "-0.038", "(0.046)"),
        ("X₂ Retained earnings / total assets",     "1.4", "-0.031", "(0.043)"),
        ("X₃ EBIT / total assets",                  "3.3", "0.355",  "1.172"),
        ("X₄ Market equity / total liabilities",    "0.6", "3.860",  "2.316"),
        ("X₅ Sales / total assets",                 "1.0", "0.052",  "0.052"),
    ]) }}
```

Rules: name the VARIANT — Altman has separate coefficients for manufacturing,
non-manufacturing and emerging markets, and using the wrong one silently
invalidates the score. Contributions must sum to the score. Never invent a
composite: if you are weighting criteria of your own, use `scorecard`, which is
honest about being a judgement. State in `note` which single input is carrying
the result, because that is what a reader monitors. These scores were fitted on
particular samples in particular decades — a bank or a software company scored
on the manufacturing Z-score is a category error, and if you do it anyway, say
so.
