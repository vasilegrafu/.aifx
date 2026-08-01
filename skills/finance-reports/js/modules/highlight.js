/* docs-html/highlight — runtime syntax coloring, shared by the code blocks in
   documents and the diagram source editor (diagrams.js).

   Documents hold code as PLAIN TEXT and declare the language with a data-lang
   attribute (`<pre><code data-lang="python">`); no token markup, no
   `language-*` classes are ever authored. This feature adds what Prism needs
   at runtime and colors in place. The palette lives in css/modules/code.css.

   Engine: Prism core + its autoloader (~7KB), lazy from CDN — a document
   without `data-lang` code fetches nothing. The autoloader then pulls each
   language grammar (python, sql, mermaid, …) on demand from the pinned
   components path. If the CDN is unreachable, code simply stays plain. */

"use strict";

(() => {
  const PRISM = "https://cdn.jsdelivr.net/npm/prismjs@1.29.0";
  let ready = null;

  docsHtml.highlight = {

    /** Load Prism core + autoloader once; resolves when highlighting works. */
    ensure() {
      if (!ready) {
        window.Prism = window.Prism || {};
        window.Prism.manual = true;              // we call highlightElement ourselves
        ready = docsHtml.util.loadScript(`${PRISM}/prism.min.js`)
          .then(() => docsHtml.util.loadScript(`${PRISM}/plugins/autoloader/prism-autoloader.min.js`))
          .then(() => {
            window.Prism.plugins.autoloader.languages_path = `${PRISM}/components/`;
          });
      }
      return ready;
    },

    /** Color one code element in place (grammar auto-loaded by language). */
    element(code, lang) {
      code.classList.add(`language-${lang}`);    // runtime-internal, never authored
      window.Prism.highlightElement(code);
    },
  };

  docsHtml.register({
    name: "highlight",
    selector: "code[data-lang]",

    init(codes) {
      docsHtml.highlight.ensure().then(() => {
        for (const code of codes)
          docsHtml.highlight.element(code, code.dataset.lang);
      }).catch(() => {});                        // CDN down → plain code, still readable
    },
  });
})();
