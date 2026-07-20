# checklist

_Authoring guidance for the `checklist` component — when to use it, how, and the rules._

Styled by: `css/lists.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Status-tracked items: test cases, release gates, action items. The
✓ / ○ / ✕ marks are drawn by CSS from `data-state`.

## Markup
```html
<ul class="checklist">
  <li data-state="done">TC-001 login happy path</li>
  <li data-state="pending">TC-002 wrong password</li>
  <li data-state="blocked">TC-003 SSO — awaiting test tenant</li>
</ul>
```

## States
`done` | `pending` | `blocked` — `data-state` is mandatory on every item.

## Rules
- Blocked items say what blocks them.
- Updating a state is a document modification: version bump +
  change-history row like any other edit.
