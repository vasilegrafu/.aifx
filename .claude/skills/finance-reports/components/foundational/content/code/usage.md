# code

_Authoring guidance for the `code` component — when to use it, how, and the rules._

A plain, unframed code block. For a titled block with a language label in a
title bar, use [[code-block]].

## Markup

```jinja
{% call c.code(lang="python") %}
def free_cash_flow(operating, capex):
    return operating - capex
{% endcall %}
```

## Rules

- **The body is literal text, and the environment does not escape it.** With
  `autoescape=False`, a `<` in the code is markup unless you write `&lt;` —
  so anything containing tags needs escaping by hand or it will disappear
  into the page.
- **`lang=` only sets `data-lang`.** Colouring happens at view time from that
  attribute; an unrecognised or omitted value renders as plain text rather
  than failing, so a wrong `lang` is silent.
- **Indentation inside the `{% call %}` is preserved verbatim**, including the
  leading whitespace of the template. Start the body at column zero or the
  block inherits the template's indentation.
- Use [[code-block]] when the reader needs to know what file or language they
  are looking at — a bare block with no title makes that the caption's job,
  and captions are easy to lose.
