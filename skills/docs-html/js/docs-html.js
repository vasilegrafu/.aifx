/* docs-html.js — the single script every document links; the entry that loads
   the real code from js/modules/, exactly like css/docs-html.css @imports its
   css/modules/. NO logic lives here — only the module list and the injector.

   MODULES order IS the dependency order (core first, main last); async=false
   makes the injected classic scripts execute in that order. Classic <script>
   injection (not ES modules) because documents open via file://, where module
   imports are blocked by the browser's opaque-origin rule.

   The base URL is taken from this script's own src, so the same file works
   with the relative href, the cross-drive file:/// href, and a future CDN URL.

   Adding a feature: create js/modules/<name>.js (it registers itself with
   docsHtml.register — see core.js), then add <name> here. Nothing else. */

(function () {
  var MODULES = ["core", "util", "icons", "layout-toggle", "highlight", "math", "diagrams", "chart", "main"];
  var base = document.currentScript.src.replace(/docs-html\.js[^/]*$/, "");
  MODULES.forEach(function (name) {
    var s = document.createElement("script");
    s.src = base + "modules/" + name + ".js";
    s.async = false;             // preserve execution order
    document.head.appendChild(s);
  });
})();
