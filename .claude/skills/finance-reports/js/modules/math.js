/* docs-html/math — LaTeX formulas rendered at view time by KaTeX.

   Markup (plain LaTeX text in the document, no images, no per-document JS):
     <div class="math">…LaTeX…</div>    display formula, own line
     <span class="math">…LaTeX…</span>  inline, inside prose

   KaTeX (script + stylesheet + its fonts) loads from the pinned CDN only when
   the document actually contains a .math element. If the CDN is unreachable,
   the raw LaTeX stays visible in mono type (styled by math.css) — readable,
   never broken. */

"use strict";

(() => {
  const KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist";

  docsHtml.register({
    name: "math",
    selector: ".math",

    init(nodes) {
      Promise.all([
        docsHtml.util.loadStyle(`${KATEX}/katex.min.css`),
        docsHtml.util.loadScript(`${KATEX}/katex.min.js`),
      ]).then(() => {
        for (const el of nodes) {
          window.katex.render(el.textContent, el, {
            displayMode: el.tagName !== "SPAN",   // span = inline, anything else = display
            throwOnError: false,                  // bad TeX renders red, page survives
          });
        }
      }).catch(() => {});                         // CDN down → plain LaTeX stays readable
    },
  });
})();
