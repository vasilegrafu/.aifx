# timeline

Styled by: `css/blocks.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

A vertical sequence of dated points on a rail — project milestones, a
release history, a roadmap, an incident timeline.

## Markup
```html
<ol class="timeline">
  <li data-state="done">
    <span class="when">2026-Q1</span>
    <h3>Importer rewrite shipped</h3>
    <p>All eight domains on the new session builder.</p>
  </li>
  <li data-state="current">
    <span class="when">2026-Q3</span>
    <h3>Portfolio app v2</h3>
    <p>webapi + webapp split; v1 kept read-only.</p>
  </li>
  <li>
    <span class="when">2026-Q4</span>
    <h3>Research workspace</h3>
    <p>Planned.</p>
  </li>
</ol>
```

## State
| `data-state` | Node |
|---|---|
| _(none)_ | outlined dot — upcoming / planned |
| `done` | filled dot — completed |
| `current` | ringed dot — in progress now |

## Rules
- Chronological order, top to bottom. `when` is a stable label (ISO date,
  quarter, version) — not prose.
- One event per `<li>`; keep the body to a line or two.
- For dependency graphs rather than a straight sequence, use a Mermaid
  diagram ([[diagram-mermaid]]) instead.
