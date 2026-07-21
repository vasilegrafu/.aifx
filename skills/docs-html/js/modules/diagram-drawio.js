/* docs-html/diagram-drawio — freeform draw.io / diagrams.net diagrams.

   Markup (the mxGraph XML as plain text — the editable source):
     <pre class="drawio"><mxGraphModel>…</mxGraphModel></pre>

   This module only turns mxGraph XML into an <svg> and hands it to the shared
   viewport (diagrams.js), which owns pan/zoom, the toolbar, fullscreen,
   download and copy. What IS draw.io-specific lives here: the engine pin and
   the offscreen render.

   The diagrams.net bundle (~3.6 MB) loads from the pinned CDN only when the
   document holds a .drawio element, and we use ONLY its mxGraph — never its own
   viewer chrome. The SVG we build carries a viewBox, so 100% fits the column
   width with proportional height. Unreachable CDN or bad XML → the source stays
   visible as a code box (diagram-drawio.css).

   Unlike Mermaid, draw.io XML is machine geometry, not prose: explicit
   coordinates, edited as XML, never auto-laid-out. */

"use strict";

(() => {
  const VIEWER = "https://cdn.jsdelivr.net/gh/jgraph/drawio@24.7.17/src/main/webapp/js/viewer-static.min.js";
  const PAD = 12;                                  // viewBox breathing room around the graph
  const PAD_TOP = 46;                              // …plus a band the floating toolbar sits in,
                                                   // so it never covers the top of the diagram

  /** mxGraph XML → a standalone, responsive SVG (viewBox, width:100%, height:auto).
      Rendered offscreen; returns null if the model is empty. */
  function renderSvg(xml) {
    const doc = window.mxUtils.parseXml(xml);
    const off = document.createElement("div");
    off.style.cssText = "position:absolute;visibility:hidden;left:-9999px;top:0;";
    document.body.appendChild(off);
    try {
      const graph = new window.mxGraph(off);
      graph.setEnabled(false);
      new window.mxCodec(doc).decode(doc.documentElement, graph.getModel());
      const b = graph.getGraphBounds();
      const svg = off.querySelector("svg");
      if (!svg || !b || !b.width || !b.height) return null;
      svg.setAttribute("viewBox",
        `${b.x - PAD} ${b.y - PAD_TOP} ${b.width + 2 * PAD} ${b.height + PAD_TOP + PAD}`);
      svg.removeAttribute("width");
      svg.removeAttribute("height");
      svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
      svg.style.cssText = "width:100%;height:auto;display:block;";
      svg.remove();                                // detach; the Viewer re-homes it
      return svg;
    } finally {
      off.remove();
    }
  }

  docsHtml.register({
    name: "diagram-drawio",
    selector: "pre.drawio",

    init(nodes) {
      const pres = [...nodes].filter((p) => p.textContent.trim());
      if (!pres.length) return;

      docsHtml.util.loadScript(VIEWER).then(() => {
        let index = 0;
        for (const pre of pres) {
          const xml = pre.textContent.trim();
          let svg = null;
          try { svg = renderSvg(xml); } catch (e) { svg = null; }
          if (!svg) continue;                      // bad XML → leave the source visible

          try {
            new docsHtml.diagram.Viewer({
              pre, svg, index: ++index,
              source: xml,
              copyTitle: "copy draw.io XML",
            });
          } catch (e) {
            pre.hidden = false;                    // wiring failed → restore the source
          }
        }
      }).catch(() => {});                          // CDN down → the XML source stays readable
    },
  });
})();
