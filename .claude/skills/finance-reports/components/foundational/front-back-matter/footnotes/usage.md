# footnotes

_Authoring guidance for the `footnotes` component — when to use it, how, and the rules._

Styled by: `css/foundational/blocks.css`

Numbered notes at the end of a document (or section), each with a ↩ link back
to its reference point.

## Markup

The inline marker is hand-written in the prose:

```html
…as reported<sup class="fn"><a id="fnref-1" href="#fn-1">1</a></sup> in Q2…
```

and the list goes at the end:

```jinja
{{ c.footnotes(["The figure excludes one-off items.", "Company filings, 10-K 2025."]) }}
```

## Rules

- **Numbering is positional — note N is marker N.** Nothing links the two but
  their order, so when you insert or delete a note, renumber both sides in the
  same edit.
- **Footnotes are for asides and caveats; [[references]] is for citations.**
  Mixing them means a reader checking a source has to read every aside to find
  it.
- **More than about ten footnotes usually means the asides belong in the
  text.** A note the argument depends on is not an aside.
- Distinct from `footnote_disclosures`, which reproduces the numbered notes to
  a set of financial statements and is a statement's cross-reference target.
