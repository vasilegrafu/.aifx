# toc

Styled by: `css/toc.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Static table of contents — written and maintained by hand (or by Claude),
NEVER generated at runtime. Placed immediately after the
[[metadata-header]].

## Markup
```html
<nav class="toc">
  <p class="toc-title">Contents</p>
  <ul>
    <li><a href="#context">Context</a></li>
    <li><a href="#decision">Decision</a>
      <ul><li><a href="#decision-rationale">Rationale</a></li></ul>
    </li>
  </ul>
</nav>
```

## Rules
- One entry per [[section]] `<h2>`; nest an inner `<ul>` for `<h3>`
  subsections when they help navigation.
- MUST be updated in the same edit that adds, renames, or removes a
  section — `audit` checks entries match the sections exactly (ids and
  titles).
- Regular documents have exactly one; presentations have none.
