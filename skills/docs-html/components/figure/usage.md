# figure

Styled by: `css/content.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Captioned image — screenshots, photos, hand-drawn SVG exports. For
anything expressible as text, use [[diagram-mermaid]] instead.

## Markup
```html
<figure>
  <img src="login-screen.png" alt="Login screen">
  <figcaption>Login screen — error state</figcaption>
</figure>
```

## Rules
- `alt` text and `<figcaption>` are mandatory.
- Image files live next to the document in `docs/` (export embeds them
  as data URIs).
