# numbered

_Authoring guidance for the `numbered` component — when to use it, how, and the rules._

An ordered list (plain `<ol>`). Use when the order is part of the meaning, or
when the reader needs to refer back to an item by its number.

## Markup

```jinja
{{ c.numbered(items=[
    "Margin recovered before volume did.",
    "The buyback resumed only after that.",
    "Guidance was raised last, once both were established.",
]) }}
```

## Rules

- **Number only what is ordered.** Numbering unordered points invents a
  ranking, and a reader will try to interpret it. Use [[bullets]] instead.
- **A procedure is not an ordered list.** Use [[steps]] for something the
  reader performs, [[checklist]] for pass/fail state. Ordering alone is not
  what makes a procedure readable.
- **Numbers are for citing, so keep them stable.** If body text says "point
  3", inserting an item silently rewrites that reference — prefer naming the
  point over numbering it when the body has to link back.
- Keep items to a sentence or two. An item that runs to a paragraph is a
  [[subsection]] wearing a number.
