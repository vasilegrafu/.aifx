# glossary

Styled by: `css/blocks.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Defined terms and acronyms — a back-matter section in formal documents, and
inline first-use definitions in the body.

## Glossary section
```html
<dl class="glossary">
  <dt id="term-adr">ADR</dt>
  <dd>Architecture Decision Record — a dated, immutable record of one
      significant decision and its context.</dd>
  <dt id="term-cgnat">CGNAT</dt>
  <dd>Carrier-Grade NAT — ISP-side address sharing that breaks per-connection
      session affinity.</dd>
</dl>
```

## Inline first-use definition
```html
The <dfn>fit criterion</dfn> is the measurable pass/fail test for a requirement.
```

## Rules
- Alphabetical order in the glossary section.
- Give each `<dt>` an `id` (`term-<slug>`) so body text can link to it.
- Define an acronym once inline with `<dfn>` at first use, and once in the
  glossary — the writing-style contract still requires the first-use
  expansion in running text.
- A term with no definition does not belong in the glossary.
