# change-history

Styled by: `css/metadata.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

The document's version log — who changed what, when. Lives inside the
[[metadata-header]], after the `<dl>`.

## Markup
```html
<table class="change-history">
  <caption>Change history</caption>
  <thead><tr><th>Version</th><th>Date</th><th>Author</th><th>Change</th></tr></thead>
  <tbody>
    <tr><td>0.1</td><td>2026-07-16</td><td>Vasile Grafu</td><td>Initial draft</td></tr>
  </tbody>
</table>
```

## Rules
- Newest row last.
- Every modification appends a row and bumps the Version in the `<dl>` —
  the two must never disagree.
- Required for every document past v0.x; optional (usually absent) for a
  fresh 0.1 draft.
