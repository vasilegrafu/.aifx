# revision-note

_Authoring guidance for the `revision-note` component — when to use it, how, and the rules._

Styled by: `css/blocks.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

An inline annotation marking what changed in a specific revision, placed
next to the affected content. Lighter than a [[callout]] — it documents an
edit, it does not warn. Complements the change-history table: the table says
*that* a version changed, the note says *what* changed *here*.

## Markup
```html
<p class="revision-note" data-rev="v1.2">
  Retry policy clarified after the 2026-06 review: 3 attempts, 30 s backoff.
</p>
```

The `data-rev` value becomes the "REVISION v1.2" label (CSS-injected).

## Rules
- Always set `data-rev` — without it the label reads just "Revision".
- Keep it to one or two sentences describing the change, not the whole
  history.
- Remove or fold notes older than a couple of versions into prose; they are
  scaffolding for reviewers, not permanent content.
- The version in `data-rev` matches a row in the change-history table.
