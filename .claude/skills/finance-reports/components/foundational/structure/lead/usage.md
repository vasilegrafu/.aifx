# lead

_Authoring guidance for the `lead` component — when to use it, how, and the rules._

The opening summary paragraph, set in larger type. It is the first thing read
and often the only thing read.

## Markup

```jinja
{{ c.lead(text="Three years of margin expansion came from mix, not price, and
    the buyback was funded entirely from operating cash.") }}
```

## Rules

- **Once per document.** Larger type is a claim that this paragraph outranks
  the others; a second one withdraws the claim. Subsequent paragraphs are
  [[prose]].
- **State the conclusion, not the plan.** "This report examines margin,
  cash flow and valuation" tells a reader who has already seen the contents
  nothing. Lead with what was found.
- **It must survive being read alone.** Assume the reader stops here — so no
  pronoun pointing at a later section, and no forward reference to an exhibit
  they have not reached.
- Keep it to two or three sentences. A lead that fills the first screen is a
  summary section, and should be one.
- Like [[prose]], it also accepts a `{% call %}` block when the paragraph needs
  inline markup — `{% call c.lead() %}…{% endcall %}`. The emphasis comes from
  the `lead` class, never from a heading tag used for its size.
