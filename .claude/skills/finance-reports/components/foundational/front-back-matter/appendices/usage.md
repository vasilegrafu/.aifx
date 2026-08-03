# appendices

_Authoring guidance for the `appendices` component — when to use it, how, and the rules._

The back-matter wrapper that isolates appendix lettering from the body's
section numbering. A `{% call %}` container holding one or more [[appendix]]
sections. Styled by: `css/foundational/blocks.css`
(`.appendices > section.appendix`).

## Markup

```jinja
{% call c.appendices() %}
  {% call c.appendix("appendix-schema", "Data model") %}...{% endcall %}
  {% call c.appendix("appendix-config", "Config reference") %}...{% endcall %}
{% endcall %}
```

## Rules

- **All appendices share ONE wrapper.** The `.appendices` div carries the
  `counter-reset`, so wrapping each appendix separately restarts the counter
  and every one of them letters as A. This is the single failure this
  component exists to prevent.
- **The wrapper goes after the body, not inside it.** Its whole job is to
  isolate lettering from the body's section numbering; nested in a section, it
  inherits the numbering it was meant to escape.
- **Empty wrapper, no output worth having.** A call with no [[appendix]] inside
  emits a bare container — the page renders, and the back matter is silently
  missing.
