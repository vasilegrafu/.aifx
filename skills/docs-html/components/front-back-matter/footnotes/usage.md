# footnotes

_Authoring guidance for the `footnotes` component — when to use it, how, and the rules._

Styled by: `css/modules/blocks.css`

Numbered notes at the end of a document (or section), each with a ↩ link back
to its reference point. The inline marker is hand-written in the prose:

```html
…as reported<sup class="fn"><a id="fnref-1" href="#fn-1">1</a></sup> in Q2…
```

and the list at the end:

`{{ c.footnotes(["The figure excludes one-off items.", "Company filings, 10-K 2025."]) }}`

Rules: numbering is positional (note N = marker N) — keep both in the same
order when editing; use footnotes for asides and caveats, References for
citations; more than ~10 footnotes usually means the asides belong in the
text.
