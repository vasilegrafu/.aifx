# section

Styled by: `css/base.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

The structural unit of a document. Everything after the [[toc]] is
sections; all other content components live inside them.

## Markup
```html
<section id="context">
  <h2>Context</h2>
  <p>…</p>
  <section id="context-constraints">
    <h3>Constraints</h3>
    <p>…</p>
  </section>
</section>
```

## Rules
- `id` = slug of the heading (lowercase, hyphens); child ids are prefixed
  with the parent id.
- Headings `<h2>`–`<h4>` only — `<h1>` belongs to the [[metadata-header]].
- Every `<h2>` section appears in the [[toc]].
- Optional numbering: `class="numbered"` on `<body>` numbers h2/h3 via CSS
  counters (formal documents like an SRS, where "see section 3.2" matters).
