/* docs-html/layout-toggle — the ▯ page-width / ▭ full-width switch.
   Activated by the .doc-toolbar markup base.html.j2 writes into every
   non-presentation document. Only flips the body class; which button looks
   active is decided purely in CSS from that class. */

"use strict";

docsHtml.register({
  name: "layout-toggle",
  selector: ".doc-toolbar",

  init(toolbars) {
    for (const toolbar of toolbars) {
      toolbar.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-w]");
        if (!btn) return;
        document.body.classList.toggle("wide", btn.getAttribute("data-w") === "wide");
      });
    }
  },
});
