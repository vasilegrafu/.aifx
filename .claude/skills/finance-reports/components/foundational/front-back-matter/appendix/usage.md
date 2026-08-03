# appendix

_Authoring guidance for the `appendix` component — when to use it, how, and the rules._

A back-matter appendix section, auto-lettered "Appendix A." and so on. A
`{% call %}` container wrapping the appendix body; it emits only the
`<section class="appendix">`.

## Markup

```jinja
{% call c.appendices() %}
  {% call c.appendix("appendix-schema", "Data model") %}
    {{ c.prose(text="Every field the report reads, and where it comes from.") }}
  {% endcall %}
{% endcall %}
```

## Rules

- **It MUST sit inside a `{% call c.appendices() %}` block.** The lettering
  counter lives on the [[appendices]] wrapper, not here — outside one, or in a
  wrapper of its own, it resets to A.
- **The `id` is what the body links to, so make it permanent.** Prefix it
  `appendix-` and name it for the content; the letter is generated from
  position and changes whenever an appendix is inserted, so nothing may
  reference "Appendix B" as an address.
- **An appendix holds what the argument does not need.** Material the reader
  must read to follow the finding belongs in the body — an appendix is where
  evidence goes to be checkable, not where a section goes to be shortened.
