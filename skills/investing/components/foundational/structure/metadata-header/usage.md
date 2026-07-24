# metadata-header

_Authoring guidance for the `metadata-header` component — when to use it, how, and the rules._

Styled by: `css/metadata.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

The document's title block — always the first element in `<body>`. Carries
the document-type kicker and the title. In print it becomes the cover page.

## Markup
```html
<header class="doc-meta">
  <p class="doc-type">Architecture Decision Record</p>
  <h1>Message Queue Selection</h1>
</header>
```

## Adding facts to the cover

The composed header carries **no Author / Date / Version**. Those were
removed in 4.0.0: composed into every document, they were a name from
`git config`, the date the *skeleton* was generated rather than the day the
content was written, and a version stuck at `0.1` unless someone remembered
to bump it. A fact nobody maintains is worse than an absent one, because a
reader trusts it.

Add facts by hand when the document genuinely carries them, as a `<dl>` after
the `<h1>` — the CSS styles it as an aligned label/value grid:

```html
<header class="doc-meta">
  <p class="doc-type">Architecture Decision Record</p>
  <h1>Message Queue Selection</h1>
  <dl>
    <dt>Owner</dt>      <dd>Platform team</dd>
    <dt>Reviewers</dt>  <dd>Jane Doe, John Roe</dd>
    <dt>Supersedes</dt> <dd><a href="adr-003.html">ADR-003</a></dd>
  </dl>
</header>
```

Typical pairs: `Owner`, `Reviewers`, `Approved by`, `Supersedes` /
`Superseded by` (ADRs — as links), `Effective` / `Review by` (policies).
Write only what someone will keep current.

## Rules
- Exactly one per document; the `<h1>` inside it is the document title
  (no other `<h1>` anywhere).
- No organization line: one was printed above every title until 4.0.0 and was
  removed. A document that must name its organization writes it in the content.
- `doc-type` kicker: the document type in full words, uppercase-styled by
  CSS — write normal case.
- Any date is ISO format (`YYYY-MM-DD`).
- A document that tracks revisions uses [[change-history]] inside this
  header, after the title (or after the `<dl>` if there is one) — dated per
  row, which is the honest place for a date and a version.
