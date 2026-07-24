/* docs-html/attr-fallback — makes the data-attribute bar geometry work outside
   Chromium. A polyfill with a shelf life: delete this file the day Firefox and
   Safari ship typed attr().

   Bar widths, bar offsets and plot positions are computed at compose time and
   carried as data- attributes, because the authoring contract forbids style=
   (SKILL.md). CSS reads them back with `width: attr(data-pct type(<percentage>),
   0%)` — CSS Values 5, shipped in Chromium 133, nowhere else yet.

   The failure is not graceful, which is why this file exists. An engine that
   cannot parse the declaration drops it whole — the 0% fallback lives INSIDE
   the syntax it cannot parse — so width reverts to auto and the bar fills its
   track. Every bar then renders full width: a bridge shows +13,031 and +4,200
   as the same size. Wrong data, not missing data.

   So: detect once, and where the CSS cannot do the job, set the equivalent
   inline style. Chromium never enters this path and keeps the pure-CSS
   rendering. Setting styles at runtime is not a contract breach — the contract
   governs what a document's SOURCE contains; charts.js already sizes its canvas
   the same way.

   THE INVARIANT: the attribute name alone determines the property, everywhere
   in the system. That is what lets this file select on the attribute instead of
   duplicating fourteen components' class names. Adding a geometry attribute
   means adding it to GEOMETRY below and nowhere else — but never reuse one of
   these six names for anything that is not that property. */

"use strict";

docsHtml.register({
  name: "attr-fallback",
  selector: "[data-pct],[data-lo],[data-span],[data-at],[data-x],[data-y]",

  init(targets) {
    // Mirrors the declarations in investing.css and blocks.css exactly.
    const GEOMETRY = {
      pct:  "width",         // every *-fill and .funnel-bar
      lo:   "margin-left",   // .bridge-bar, .valrange-bar — offset within the track
      span: "width",         // .bridge-bar, .valrange-bar
      at:   "left",          // .valrange-mark
      x:    "left",          // .quadrant-item
      y:    "bottom",        // .quadrant-item
    };

    // One probe for the whole document. No CSS.supports at all (pre-2015
    // engines) also means no typed attr(), so treat that as unsupported.
    const supported = typeof CSS !== "undefined"
      && typeof CSS.supports === "function"
      && CSS.supports("width", "attr(data-pct type(<percentage>), 0%)");
    if (supported) return;

    // Compose time already rounded these; anything else is not ours to apply.
    const PERCENTAGE = /^-?\d+(\.\d+)?%$/;

    for (const el of targets)
      for (const key in GEOMETRY) {
        const value = el.dataset[key];
        if (value && PERCENTAGE.test(value))
          el.style.setProperty(GEOMETRY[key], value);
      }
  },
});
