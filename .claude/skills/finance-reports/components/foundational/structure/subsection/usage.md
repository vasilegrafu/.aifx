# subsection

_Authoring guidance for the `subsection` component — when to use it, how, and the rules._

A nested section with an `<h3>` heading — the second level of document
structure, inside a [[section]].

## Markup

```jinja
{% call c.subsection("margin-mix", "Margin came from mix") %}
  {{ c.prose(text="Price held flat across all three years.") }}
{% endcall %}
```

## Rules

- **The `id` is a permanent address.** The table of contents and every in-page
  link resolve against it, and a report reports an **error** on its own first
  screen for a link that lands nowhere. Renaming a heading is free; renaming its
  `id` breaks whatever already points at it.
- **Give it an `id` that names the finding, not the position.** `margin-mix`
  survives a reordering; `section-3` is wrong the moment anything moves.
- **A subsection needs a sibling.** One subsection inside a section is a
  heading that adds a level of hierarchy without dividing anything — put the
  content directly in the [[section]] instead.
- It emits a container and nothing else: the body comes from the `{% call %}`
  block, so its children are ordinary component calls with their own rules.
