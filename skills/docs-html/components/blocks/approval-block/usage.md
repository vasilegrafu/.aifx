# approval-block

_Authoring guidance for the `approval-block` component — when to use it, how, and the rules._

Styled by: `css/metadata.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Signature grid for documents requiring formal sign-off (project charter,
SLA, release approval, test report acceptance). Placed in a closing
`<section id="approvals">` at the end of the document.

## Markup
```html
<section id="approvals">
  <h2>Approvals</h2>
  <table class="approvals">
    <thead><tr><th>Name</th><th>Role</th><th>Date</th><th>Signature</th></tr></thead>
    <tbody>
      <tr><td>Jane Doe</td><td>Author</td><td></td><td></td></tr>
      <tr><td></td><td>Product Owner</td><td></td><td></td></tr>
    </tbody>
  </table>
</section>
```

## Rules
- Date and Signature cells stay EMPTY in the source — they are filled on
  the printed/PDF copy by the signers (the tall bordered cells are the
  signing lines).
- A signed document's content changes only via a new version with a new
  approval round (record it in the change-history).
- Include in the [[toc]] like any section.
