# callout

Styled by: `css/callouts.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Highlighted box for content that must not be skimmed past. The label
("Note", "Warning", …) is added by CSS — write only the body.

## Markup
```html
<aside class="decision"><p>We will use PostgreSQL.</p></aside>
```

## Variants
| Class | Use for |
|---|---|
| `note` | supplementary context the reader may want |
| `warning` | consequences if ignored (deployment, runbooks) |
| `decision` | the key decision of a section; exactly one per ADR |
| `risk` | an open risk — `audit` collects these across all documents |

## Rules
- Never nested; no headings inside.
- A section that is mostly callouts should be rewritten as prose.
