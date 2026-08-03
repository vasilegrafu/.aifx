# peer-comparison

_Authoring guidance for the `peer-comparison` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/fundamental-analysis.css`

The subject company set against its named comparables on whatever metrics
decide the argument — growth, margin, returns, leverage, multiple. The subject
row is highlighted so the eye finds it without hunting.

## Markup

```jinja
{{ c.peer_comparison(
    caption="Mega-cap platforms — FY2025 reported, ordered by market cap",
    headers=["Revenue growth", "Gross margin", "Operating margin", "ROIC", "Net cash", "P/E (NTM)"],
    rows=[
        ("Apple",     ["+6.4%",  "46.9%", "32.0%", "58%", "$51B",  "31.2x"], True),
        ("Microsoft", ["+15.7%", "69.4%", "45.6%", "29%", "$26B",  "33.8x"], False),
        ("Alphabet",  ["+13.9%", "58.2%", "32.1%", "31%", "$83B",  "23.1x"], False),
        ("Peer median", ["+13.9%", "58.2%", "32.1%", "31%", "$51B", "31.2x"], False),
    ]) }}
```

## Rules

- **Name the peer set and justify it in one line.** Comparables chosen after
  the fact prove whatever you want — the peer group is a choice, not a screen.
- **Same period and same accounting basis for every row.** If one peer has a
  different fiscal year, say so in the caption.
- **Include a median row** so the reader sees the reference point you are using
  in `valuation_multiples`.
- **Six metrics is the practical maximum** before the table needs `wide` mode.
- **Never highlight more than one subject row.**
