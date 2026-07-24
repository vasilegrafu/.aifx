# sankey

_Authoring guidance for the `sankey` component — when to use it, how, and the rules._

A flow diagram: how a total splits, merges or converts as it moves across
stages. Revenue becoming net income. Cash sources becoming uses. Capital
allocated across segments. Rendered by [[apache-echarts]] through the
shared frame, so it carries the same toolbar and the same degradation path.

**Use when** the question is *where did it go* — and the answer is a chain, not
a list. A single split is a stacked bar; a decomposition of one total into
another is [[bridge]]. Sankey earns its width when value passes through two or
more stages.

## Markup

```html
{% raw %}{{ c.sankey(
     nodes=[("Revenue", "source"), ("Gross profit", "stage"),
            ("Cost of sales", "cost"), ("Operating expenses", "cost"),
            ("Net income", "retained")],
     links=[("Revenue", "Cost of sales", 210352),
            ("Revenue", "Gross profit", 180683),
            ("Gross profit", "Operating expenses", 57467),
            ("Gross profit", "Net income", 123216)],
     caption="FY2025 revenue to net income ($M)",
     note="Every dollar of revenue is either consumed or retained.") }}{% endraw %}
```

- `nodes` — `(name, role)`. Names are the join key: a link's `source` and
  `target` must match a node name exactly.
- `links` — `(source, target, value)`.
- `height` (default `420`) — sankeys need vertical room; a cramped one is
  unreadable.

## Roles, not identities — the whole point

The four roles are `source`, `stage`, `cost`, `retained`, and they map to
design colours, not to the categorical palette:

| role | colour | meaning |
|---|---|---|
| `source` | `palette:1` | value entering the system |
| `stage` | `token:muted` | an intermediate total, carrying value onward |
| `cost` | `token:caution` | value leaving the system |
| `retained` | `token:positive` | value kept |

This is what makes the component necessary. Left to itself, ECharts assigns a
categorical colour per node, so a fifteen-node sankey cycles an eight-slot
palette and two unrelated nodes come out the same hue — "iPhone" and "Operating
expenses" wearing one colour, implying a relationship that does not exist.
Colouring by role means the number of colours never depends on the number of
nodes.

`cost` uses the caution tone and `retained` the positive tone. That is a
**direction** encoding — value leaving versus value kept — which is the
documented exception to *status colours are reserved*. It is not a judgement:
cost of sales is not a bad thing, it is an outgoing thing.

## It also serves a stock — at a price

The roles describe a flow, but the shape works for a **balance sheet** too:
assets in on the left, `Total assets` as the stage, liabilities (`cost`) and
equity (`retained`) as the claims on the right. The accounting equation is a
conservation law, so the diagram balances by construction, and it answers *how
much of what it owns does the company actually own?* at a glance.

The price is that **nothing moves**. A stock has no direction, so the source →
cost reading that makes an income sankey legible is a metaphor here. Say so in
the `note`, especially when a flow sankey appears earlier in the same document
— a reader trained on that one will read movement into this one. Do not reach
for this shape for a stock whose parts do not sum to a meaningful whole.

## Rules

- **Conservation.** Inflows must equal outflows at every intermediate node. A
  sankey that does not balance is a chart that lies, and nothing in the
  rendering will tell you — check the arithmetic before you publish.
- **No cycles.** Value flows one way. If your data loops, it is a graph, not a
  sankey — use [[mermaid]].
- **Name the totals in the node labels**, not just the categories: a reader
  should be able to add up a stage without hovering.
- **State the conclusion in `note`.** The diagram shows the shape; the sentence
  says what it means. A sankey without a reading is decoration.
- Do not set colours per node. The role does it. If a node does not fit one of
  the four roles, the flow is probably modelled wrong.
