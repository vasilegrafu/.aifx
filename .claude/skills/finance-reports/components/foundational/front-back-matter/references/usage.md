# references

_Authoring guidance for the `references` component — when to use it, how, and the rules._

Back-matter numbered citations, numbered `[n]` automatically.

## Markup

Each item is a **mapping with `id` and `text`**, not a tuple — the macro reads
`it.id` and `it.text` by attribute, so a `(id, text)` pair raises under
`StrictUndefined` rather than rendering:

```jinja
{{ c.references(items=[
    {"id": "ref-10k", "text": "Apple Inc., Form 10-K for FY2025, filed 2025-10-31, page 35."},
    {"id": "ref-fmp", "text": "Financial Modeling Prep, income-statement endpoint, retrieved 2026-08-03."},
]) }}
```

## Rules

- **Every item needs an `id`, prefixed `ref-`.** The number `[n]` is generated
  from position, so the `id` is the only stable handle the body can link to —
  and inserting a citation renumbers every one after it.
- **Cite the retrieval, not just the source, for anything live.** A figure
  pulled from an API is reproducible only with the date it was pulled; the
  same endpoint returns a different number tomorrow.
- **A reference is what was actually read.** Listing a filing nobody opened to
  make the page look sourced is the one failure this section cannot recover
  from.
- Point to the page or note, not the document. "Form 10-K" is not a citation
  a reader can check in under a minute.
