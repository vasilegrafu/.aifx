# collapsible

_Authoring guidance for the `collapsible` component — when to use it, how, and the rules._

Styled by: `css/content.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Progressive disclosure for depth a first-pass reader can skip — full
payloads, long logs, derivations. Native HTML `<details>`, no JavaScript.

## Markup
```html
<details>
  <summary>Full error payload</summary>
  <pre><code>{ "error": "rate_limited", "retry_after": 30 }</code></pre>
</details>
```

## Rules
- Never hide decisions, warnings, or requirements inside one — collapsed
  content is optional content.
- The `<summary>` must say what's inside, not "click here".
