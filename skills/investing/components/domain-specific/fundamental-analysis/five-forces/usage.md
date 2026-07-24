# five-forces

_Authoring guidance for the `five-forces` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Porter's five forces, each rated and evidenced, from the incumbent's point of
view. Where `swot_grid` (business category) inventories what a company has,
this examines the STRUCTURE of the industry it sits in — and structure is what
determines whether high returns persist or get competed away.

```jinja
{{ c.five_forces(
    caption="Smartphone and platform industry structure",
    verdict="Structurally attractive for the incumbent: the binding constraint is regulation, which sits outside Porter's frame entirely and is why the DMA ruling is pillar 1's falsifier.",
    forces=[
        ("Threat of new entrants", "Low", "good",
         "Silicon design, a two-million-app ecosystem and $30B+ of annual R&D make entry uneconomic; no new entrant has taken 1% share in a decade."),
        ("Bargaining power of suppliers", "Low", "good",
         "Displays and memory are commoditised across three vendors each; in-house silicon removed the largest supplier dependency."),
        ("Bargaining power of buyers", "Moderate", "neutral",
         "Consumers are price-sensitive at the low end but switching costs are high once inside the ecosystem; carrier subsidies have largely gone."),
        ("Threat of substitutes", "Low", "good",
         "No category substitutes for the smartphone; wearables extend the platform rather than replacing it."),
        ("Competitive rivalry", "Moderate", "neutral",
         "Android competes hard on price and specification but not on ecosystem lock-in; the premium tier is effectively a duopoly."),
    ]) }}
```

Rules: rate from the INCUMBENT's perspective and keep the tone consistent with
that — "low threat of new entrants" is `good` for the company you are analysing.
Every force carries evidence with a number, a share or a name; a force rated
from intuition is worth nothing. Use a consistent rating vocabulary across a
project (Low / Moderate / High). The `verdict` is the synthesis and should say
which force actually binds — usually one does, and the other four are context.
Where the real constraint is outside the framework (regulation, technology
transition, capital access), say so rather than forcing it into a box.
