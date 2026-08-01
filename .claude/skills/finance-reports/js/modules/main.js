/* finance-reports/main — the entry point: run every registered feature once the DOM
   is ready. This file is final — new features register themselves (core.js)
   and are listed in bundle.js; main never changes. */

"use strict";

if (document.readyState === "loading")
  document.addEventListener("DOMContentLoaded", () => docsHtml.init());
else
  docsHtml.init();
