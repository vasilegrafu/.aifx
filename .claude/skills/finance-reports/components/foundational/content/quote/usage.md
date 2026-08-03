# quote

_Authoring guidance for the `quote` component — when to use it, how, and the rules._

Styled by: `css/foundational/content.css`

A pull-quote: cited words set apart from the prose, with attribution.

## Markup

```jinja
{% call c.quote(source="Nygard, 2011") %}
  …the quoted words…
{% endcall %}
```

## Rules

- **Quotes are VERBATIM.** Any edit for length or grammar goes in [brackets];
  silent tidying of someone's words is misquotation.
- **Always attribute.** Where the source is a real citation it also appears in
  [[references]], so the reader can reach the original.
- **Use sparingly.** A document of quotes is a collage, not an argument — quote
  when the exact wording is the evidence, and paraphrase otherwise.
