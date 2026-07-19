# js/ — the docs-html script, as a module tree

Every document links exactly one script, `docs-html.js`. Like the CSS entry,
it holds no logic — it loads `modules/` in list order (classic `<script>`
injection; ES modules are blocked on `file://`, where documents open).

```
docs-html.js          entry/loader: the MODULES list + injector — order IS dependency order
└── modules/
    ├── core.js       the trunk: docsHtml namespace — register(), init(), data()
    ├── util.js       leaf helpers: loadScript (deduped), copyText, downloadBlob
    ├── icons.js      the shared SVG icon set (Lucide-style strokes, currentColor)
    ├── layout-toggle.js   feature — ▯/▭ width switch   (selector: .doc-toolbar)
    ├── highlight.js       feature — runtime code coloring (selector: code[data-lang]; Prism, lazy)
    ├── diagrams.js        feature — everything diagrams (selector: pre.mermaid)
    └── main.js       docsHtml.init() on DOM-ready — final, never edited
```

## Adding a feature

Create `modules/<name>.js` and add `<name>` to `MODULES` in `docs-html.js`
(before `main`). Nothing else changes — not `core.js`, not `main.js`, not any
other feature. Skeleton:

```js
/* docs-html/<name> — one sentence: what it does, what markup activates it. */

"use strict";

docsHtml.register({
  name: "<name>",
  selector: "<the markup hook>",     // no match in the document → feature dormant

  init(targets) {                    // the matched NodeList, once, on DOM-ready
    for (const el of targets) {
      // read options from the element's own data- attributes:
      // const depth = docsHtml.data(el, "depth", 2);
      // wire behaviour…
    }
  },
});
```

## The rules

1. **Self-contained.** Everything the feature needs — constants, CDN pins,
   classes, state — lives in its one file. It never reaches into another
   feature.
2. **Markup activates, never configures in JS.** A document opts in by writing
   markup; per-document tuning is `data-` attributes on that markup, read via
   `docsHtml.data(el, "option-name", fallback)`. There is no per-document
   JavaScript, ever.
3. **Own your engines.** A heavy library loads from a pinned CDN URL inside the
   feature's `init` via `docsHtml.util.loadScript(...)` (deduplicated — shared
   engines load once). A document without the feature's markup fetches nothing.
4. **Degrade gracefully.** `core.init()` isolates each feature in try/catch —
   but design the CSS-only fallback too (like `pre.mermaid` staying a readable
   code box when the CDN is unreachable).
5. **Declarative internals.** Repetitive UI (toolbars, button rows) is a data
   spec walked by a generic builder — see `DiagramViewer.BUTTONS` in
   `diagrams.js`, the reference example.

When the CDN + versioning arrive, each module becomes a real ES module
(`register` → `export`, the loader → `import` list); the tree is already the
right shape for that split.
