# todo-marker

Styled by: `css/callouts.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

The ONLY way to mark uncertain or unfinished content. The "TODO:" prefix
is added by CSS — write only what is needed.

## Markup
```html
<mark class="todo">Verify: does the gateway retry on 429?</mark>
```

## Rules
- Write a targeted instruction ("what belongs here + candidates spotted"),
  never a bare "TODO".
- Draft-depth generation fills every unresearched section with one of
  these; "fill the X section" resolves them one at a time.
- `audit` counts unresolved markers per document. Remove when resolved.
- Never invent content silently and never leave a section empty — mark it.
