# card

_Authoring guidance for the `card` component — when to use it, how, and the rules._

Styled by: `css/layout.css`

A titled, bordered surface that groups a few components into one visual unit. Use
it standalone to box a related cluster, or as the cell inside a [[grid]] / [[columns]].

## Markup

```html
{% raw %}{% call c.card("Key risks") %}
  {% call c.callout("risk") %}Supplier concentration…{% endcall %}
  {{ c.bullets([...]) }}
{% endcall %}{% endraw %}
```

- `title` (optional) — a small-caps header bar. Omit for a plain bordered panel.

## Rules

- **Group, don't nest layouts.** A card holds content components; don't put
  [[columns]]/[[grid]] inside a card — arrange at the section level instead.
- Keep a card focused — one idea. Many peers → a [[grid]] of cards.
- Not a callout: for a single note/warning/risk use the [[callout]] component; a
  card is for grouping several things.
- Inside a [[grid]]/[[column]] the container owns the outer spacing — the card's
  own margin is dropped automatically.
