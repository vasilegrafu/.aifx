# metadata-header

Styled by: `css/metadata.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

The document's corporate title block — always the first element in
`<body>`. Carries the organization line (injected from `brand.css`, no
markup needed), the document-type kicker, the title, and the facts a
reader needs before trusting the content. In print it becomes the cover
page.

## Markup
```html
<header class="doc-meta">
  <p class="doc-type">Architecture Decision Record</p>
  <h1>Message Queue Selection</h1>
  <dl>
    <dt>Author</dt>         <dd>Vasile Grafu</dd>
    <dt>Date</dt>           <dd>2026-07-16</dd>
    <dt>Version</dt>        <dd>0.1</dd>
  </dl>
</header>
```

## Entries
- `doc-type` kicker: the document type in full words, uppercase-styled by
  CSS — write normal case.
- Optional extra `<dt>/<dd>` pairs the document type calls for: `Reviewers`,
  `Owner`, `Supersedes` / `Superseded by` (ADRs — as links).

## Rules
- Exactly one per document; the `<h1>` inside it is the document title
  (no other `<h1>` anywhere).
- The organization name above the kicker comes from `--brand-name` in
  `css/brand.css` — never write it into documents.
- Date is ISO format (`YYYY-MM-DD`).
- Documents past v0.x add a [[change-history]] table inside this header,
  after the `<dl>`.
