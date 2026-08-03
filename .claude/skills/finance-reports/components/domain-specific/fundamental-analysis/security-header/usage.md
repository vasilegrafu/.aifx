# security-header

_Authoring guidance for the `security-header` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/fundamental-analysis.css`

The identity strip for the instrument a document analyses: ticker, company
name, exchange, and the handful of market facts a reader needs before the
first sentence. It sits directly under the document cover, once, in any
single-name document — earnings note, investment thesis, due diligence report.

## Markup

```jinja
{{ c.security_header(
    ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", asof="2026-07-17",
    facts=[
        ("Price", "$232.40"),
        ("Market cap", "$3.45T"),
        ("Sector", "Information Technology"),
        ("Fiscal year end", "September"),
    ]) }}
```

## Rules

- **One per document, never repeated per section.**
- **Every price-like fact carries the `asof` date.** An undated quote is a
  wrong quote within a day.
- **Do not put the recommendation here.** That is `recommendation`,
  deliberately a separate block so the facts and the opinion never blur
  together.
- **For a multi-name document — a portfolio review, a watchlist — use
  `holdings_table` instead.** This component names one security.
