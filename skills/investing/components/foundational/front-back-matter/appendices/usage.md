# appendices

_Authoring guidance for the `appendices` component — when to use it, how, and the rules._

The back-matter wrapper that isolates appendix lettering from the body's
section numbering. Macro: `appendices()` — a `{% call %}` container that holds
one or more [[appendix]] sections. The `.appendices` div carries the
`counter-reset`, so ALL appendices must share ONE wrapper to letter as
A, B, C… — never wrap each appendix separately.

```jinja
{% call c.appendices() %}
  {% call c.appendix("appendix-schema", "Data model") %}...{% endcall %}
  {% call c.appendix("appendix-config", "Config reference") %}...{% endcall %}
{% endcall %}
```

Styled by: `css/blocks.css` (`.appendices > section.appendix`).
