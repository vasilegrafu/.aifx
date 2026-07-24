# earnings-surprise

_Authoring guidance for the `earnings-surprise` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Reported against consensus for one earnings print, line by line, with the
surprise colored by whether it helps or hurts the thesis. The opening block of
every note on an earnings release: what was expected, what arrived, by how much.

```jinja
{{ c.earnings_surprise(
    caption="Apple", period="FQ4 2025 (quarter ended 27 Sep 2025)",
    rows=[
        ("Revenue",           "$102.1B", "$102.5B", "+0.4%",   "good"),
        ("iPhone revenue",    "$45.9B",  "$44.6B",  "-2.8%",   "bad"),
        ("Services revenue",  "$27.5B",  "$28.8B",  "+4.7%",   "good"),
        ("Gross margin",      "46.4%",   "47.2%",   "+80bp",   "good"),
        ("Diluted EPS",       "$1.66",   "$1.74",   "+4.8%",   "good"),
        ("Dec-quarter guide", "+5% y/y", "+8% y/y", "+3pp",    "good"),
    ]) }}
```

Rules: cite the consensus source and its date in a footnote — "consensus" with
no provenance is a number you chose. Tone reflects the effect on the thesis,
not the sign: a revenue beat driven by one-off channel fill can be `neutral`.
Include guidance as a row when guidance moved the stock more than the print
did, which is most of the time. Margins are surprised in basis points, not
percent of percent. Follow this block with what CHANGED in the thesis — a
surprise table with no interpretation is data, not a note.
