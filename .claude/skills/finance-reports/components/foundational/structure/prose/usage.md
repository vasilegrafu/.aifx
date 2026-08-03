# prose

_Authoring guidance for the `prose` component — when to use it, how, and the rules._

A single body paragraph — the default way ordinary narrative text enters a
document.

## Markup

```jinja
{{ c.prose(text="Operating cash covered the dividend and the buyback in each of
    the three years, so the balance sheet did no work to fund either.") }}
```

It also takes a `{% call %}` block, for a paragraph carrying inline markup:

```jinja
{% call c.prose() %}
  Operating cash covered both, so the balance sheet did <em>no</em> work.
{% endcall %}
```

## Rules

- **One paragraph per call.** The macro emits one `<p>`; passing two
  paragraphs' worth of text produces one run-on block, because the newline in
  the source is not a paragraph break in HTML. Call it twice.
- **Prose carries the argument, exhibits carry the evidence.** A paragraph
  that recites numbers already in a table beside it is duplication that will
  disagree with the table on the next rebuild — say what the numbers mean
  instead.
- **Nothing structural inside a paragraph.** The environment runs with
  `autoescape=False`, so HTML in `text` renders rather than showing as
  characters — which means the discipline is yours to keep, not the engine's.
  Inline emphasis is fine; headings, lists and tables have their own
  components, and building one by hand here bypasses the styling rules every
  other component follows.
- Use [[lead]] for the opening summary paragraph — it is larger type and is
  meant to be used once.
