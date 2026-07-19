# page

Styled by: `css/presentation.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

One presentation page — a fixed 16:9 sheet, like a PowerPoint slide. Pages
follow one another down the document; readers scroll or press
PageDown/PageUp and each page snaps into view. Pure HTML + CSS — there is
no navigation code, no counter script (the page number is a CSS counter).

Used only inside `<body class="presentation">`.

## Markup
```html
<section class="page">
  <h2>The problem</h2>
  <ul>
    <li>…</li>
  </ul>
</section>
```

## Variants
- `class="page page-title"` — the first page: vertically centered, holds
  the `<h1>` + [[metadata-header]]. In templates: `c.page(variant="title")`
  with the [[metadata-header]] macro as its body.

## Rules
- One idea per page, max ~5 bullets.
- Content must FIT the page — overflow is clipped by design, exactly like
  a real slide. A page that doesn't fit is two pages.
- First page: title page. Last page: next steps / asks.
- Other components ([[diagram-mermaid]], [[table]], [[callout]],
  [[checklist]]) are allowed inside pages; [[toc]] is not — presentations
  have no TOC.
- No speaker notes (nothing to toggle them with).
