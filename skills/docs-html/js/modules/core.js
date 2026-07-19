/* docs-html/core — the trunk of the tree: the one global namespace and the
   feature registry. Everything else is a leaf that registers itself.

   A feature is { name, selector, init }:
     name      for diagnostics
     selector  the markup hook that activates it — documents opt in by writing
               markup, never by writing JavaScript
     init(targets)  called once on DOM-ready with the matched NodeList

   Extending the system = drop a new module in js/modules/ that calls
   docsHtml.register(...), and list it in docs-html.js. core.js, main.js, and
   every other feature stay untouched. */

"use strict";

window.docsHtml = {
  features: [],

  register(feature) {
    this.features.push(feature);
  },

  /** Read a per-document option from a data- attribute, with typed fallback:
      docsHtml.data(el, "max-scale", 6) reads data-max-scale; numeric strings
      come back as numbers. This is THE way documents tune a feature — markup,
      never per-document JavaScript. */
  data(el, name, fallback) {
    const raw = el.dataset[name.replace(/-([a-z])/g, (_, c) => c.toUpperCase())];
    if (raw === undefined) return fallback;
    const n = Number(raw);
    return Number.isNaN(n) ? raw : n;
  },

  init() {
    for (const f of this.features) {
      const targets = f.selector ? document.querySelectorAll(f.selector) : null;
      if (targets && !targets.length) continue;   // markup absent → dormant
      try {
        f.init(targets);
      } catch (e) {
        // One broken feature degrades that feature only — the rest keep working.
        console.warn(`docs-html: feature "${f.name}" failed:`, e);
      }
    }
  },
};
