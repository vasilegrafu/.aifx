# diagram-drawio

_Authoring guidance for the `diagram-drawio` component — when to use it, how, and the rules._

Styled by: `css/diagrams.css`
Rendered by: the pinned diagrams.net engine, loaded by the `drawio` feature only
when the document holds a `.drawio` element (see SKILL.md). No `<script>` in the
document — the feature self-loads it. Renders **SVG** (crisp in print) into the
same bounded viewport Mermaid uses: at 100% the diagram **fits the column width**
with proportional height, and the toolbar gives zoom · fit · fullscreen ·
download SVG · copy XML (drag to pan, Ctrl+wheel to zoom).

For **freeform** diagrams — architecture, network, infrastructure, deployment —
where you want deliberate placement and rich shapes (cylinders, clouds, actors,
containers, swimlanes) that Mermaid can't do. For flow / sequence / ER / state,
prefer [[diagram-mermaid]] (auto-laid-out from relationships, far lighter).

## Markup

The body is the draw.io **mxGraph XML** — the editable source, kept in the
document. Author or edit it directly (positions and styles are explicit):

```html
{% raw %}{% call c.diagram_drawio() %}
<mxGraphModel>
  <root>
    <mxCell id="0"/><mxCell id="1" parent="0"/>
    <mxCell id="app" value="Web App" style="rounded=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
            vertex="1" parent="1"><mxGeometry x="40" y="40" width="120" height="50" as="geometry"/></mxCell>
    <mxCell id="db" value="PostgreSQL" style="shape=cylinder3;fillColor=#d5e8d4;strokeColor=#82b366;"
            vertex="1" parent="1"><mxGeometry x="240" y="35" width="90" height="70" as="geometry"/></mxCell>
    <mxCell style="edgeStyle=orthogonalEdgeStyle;endArrow=block;" edge="1" parent="1"
            source="app" target="db"><mxGeometry relative="1" as="geometry"/></mxCell>
  </root>
</mxGraphModel>
{% endcall %}{% endraw %}
```

## Degradation (automatic)

Until the viewer renders — or forever, if its CDN is unreachable — the mxGraph
XML shows as a code box (`diagrams.css`). Verbose, but the page never breaks.

## Rules

- **Diagrams are data, not pictures** — the XML source lives in the document;
  never paste a screenshot (that's [[figure]]).
- **No auto-layout.** draw.io XML carries explicit `x`/`y` on every cell — place
  them deliberately. If you just want a graph laid out for you, that's
  [[diagram-mermaid]].
- **Round-trips to the app.** Paste this XML into draw.io/diagrams.net to edit it
  visually; paste it back here. (Ask the assistant to edit the XML in place too.)
- Keep one diagram per block and readable — split a sprawling system into two.
