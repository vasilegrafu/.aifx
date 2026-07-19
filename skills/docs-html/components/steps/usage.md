# steps

Styled by: `css/lists.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Numbered procedure — deployment, recovery, setup. The numbers are drawn by
CSS counters; the markup is a plain list.

## Markup
```html
<ol class="steps">
  <li>Stop the service: <code>systemctl stop atlas</code></li>
  <li>Restore the snapshot.</li>
</ol>
```

## Rules
- One action per step, imperative voice.
- A [[callout]] warning about a step goes BEFORE the list (or before the
  relevant `<ol>` fragment) — never between `<li>` items.
