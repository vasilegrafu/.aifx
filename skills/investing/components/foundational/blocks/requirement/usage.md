# requirement

_Authoring guidance for the `requirement` component — when to use it, how, and the rules._

Styled by: `css/blocks.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

A single requirement, IEEE/ISO 29148 style: a trace-id, a title, a MoSCoW
priority, and structured fields. The staple of a Software Requirements
Specification. Each card is anchorable and referable from anywhere.

## Markup
```html
<article class="requirement" id="REQ-014">
  <header>
    <span class="req-id">REQ-014</span>
    <h3>Portfolio revaluation latency</h3>
    <span class="req-priority priority-must">Must</span>
  </header>
  <dl>
    <dt>Description</dt><dd>The displayer revalues an open portfolio within 500 ms of a price tick.</dd>
    <dt>Rationale</dt><dd>Traders act on stale marks otherwise.</dd>
    <dt>Fit criterion</dt><dd>p95 tick-to-render under 500 ms at 200 positions.</dd>
    <dt>Source</dt><dd>Trading desk review, 2026-06.</dd>
  </dl>
</article>
```

## Priority (MoSCoW)
| Class | Meaning |
|---|---|
| `priority-must` | mandatory for this release |
| `priority-should` | important, not vital |
| `priority-could` | desirable if time allows |
| `priority-wont` | out of scope this time (recorded, not built) |

## Rules
- The `id` is the trace-id (`REQ-NNN`) and is the requirement's identity —
  reference it with [[trace-id]] (`<a href="#REQ-014" data-trace="REQ-014">`).
- Keep the `<dl>` fields consistent across a document; Description +
  Fit criterion are the minimum. Add Dependencies / Verification as needed.
- One requirement per card — never bundle two behaviours.
- A fit criterion is measurable (numbers, not adjectives) or it is a goal,
  not a requirement.
