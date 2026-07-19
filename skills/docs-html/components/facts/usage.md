# facts

Styled by: `css/lists.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Key/value reference data: environments, endpoints, config values,
contacts, conventions. The staple of runbooks and deployment guides.

## Markup
```html
<dl class="facts">
  <dt>Environment</dt><dd>production</dd>
  <dt>Endpoint</dt><dd><code>https://api.example.com</code></dd>
</dl>
```

## Rules
- Keys short and stable; values may contain inline `<code>` and links.
- For comparative data (rows × columns) use [[table]] instead.
