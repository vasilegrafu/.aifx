# diagram-mermaid

_Authoring guidance for the `diagram-mermaid` component — when to use it, how, and the rules._

Styled by: `css/diagrams.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.
Rendered by: the pinned Mermaid CDN script — the ONLY JavaScript any
document may reference (see SKILL.md). Place the script as the last
element before `</body>`, only when the document has at least one diagram.

Diagrams as editable text: flowcharts, sequence, C4, ER, Gantt, state.

## Markup
```html
<pre class="mermaid">
flowchart LR
  App --> API --> DB[(PostgreSQL)]
</pre>
…
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
</body>
```

## Degradation (pure CSS, automatic)
Until Mermaid renders — or forever, if the CDN is unreachable — the block
displays its source as a readable code box (`diagrams.css` targets the
absence of `data-processed`). So write diagram source clean enough to read
as text.

## Rules
- Diagrams are never images; screenshots use [[figure]].
- Keep each diagram readable — split into two diagrams rather than cram.
- One Mermaid script per document, however many diagrams.
- No diagrams → no script, and drop the `diagrams.css` link.

## Charts: use [[chart-echarts]], not Mermaid

For real data charts — multi-series, stacked, a legend, tooltips, candlestick —
reach for [[chart-echarts]] (Apache ECharts, validated palette). Mermaid's own
`xychart-beta` / `pie` are quick illustrations only: single-series, no legend,
still "beta". Use them just for a throwaway curve inside a diagram-heavy page;
anything analytical goes to `chart-echarts`.

Still diagram-native through this viewport (pan/zoom, ✎ editor): `gantt`
(roadmaps, project plans), `sankey-beta` (cash/flow decomposition),
`quadrantChart` (2×2 positioning — see also the risk-matrix component).
