/* docs-html/diagram-mermaid — Mermaid diagrams, auto-laid-out from text.

   Markup (plain Mermaid text in the document, no per-document JS):
     <pre class="mermaid">flowchart LR
       A --> B</pre>

   This module only turns Mermaid source into an <svg> and hands it to the
   shared viewport (diagrams.js), which owns pan/zoom, the toolbar, fullscreen,
   download and copy. What IS Mermaid-specific lives here: the engine pin, the
   render call, and the ✎ live source editor.

   Mermaid runs with useMaxWidth:false, so the SVG comes out at natural pixel
   size — a node's box is the same across every diagram, and 100% means natural
   size. If the CDN is unreachable the source stays visible as a readable code
   box (diagram-mermaid.css). */

"use strict";

(() => {
  const MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js";
  const EDIT_DEBOUNCE = 400;                           // ms of typing pause before re-render
  const EDITOR = { minWidth: 256, keepDiagram: 160 };  // panel resize clamps, px

  /* ------------------------------------------------------- ✎ source editor */

  /** Splits the viewport: source panel left, diagram right. Lives here because
      re-rendering is engine-specific; everything else is the shared Viewer. */
  class SourceEditor {
    constructor(viewer) {
      this.v = viewer;
      this.panel = null;
      this.seq = 0;
    }

    toggle(btn) {
      if (this.panel) {
        this.panel.remove();
        this.panel = null;
        this.v.figure.classList.remove("editing");
        btn.setAttribute("aria-pressed", "false");
        return;
      }
      this.panel = this.#build();
      this.v.figure.insertBefore(this.panel, this.v.canvas);   // beside the diagram
      this.v.figure.classList.add("editing");
      btn.setAttribute("aria-pressed", "true");
      this.panel.querySelector("textarea").focus();
    }

    #build() {
      const panel = document.createElement("div");
      // diagram-exclude: typing and selecting in the panel must never pan.
      panel.className = "mermaid-editor diagram-exclude";

      // The editing surface is an overlay: a Prism-colored <pre><code> behind a
      // transparent-text textarea with identical metrics — native caret,
      // selection and undo, with syntax coloring underneath. The transparent
      // text switches on only once Prism has loaded (.highlighted), so an
      // unreachable CDN degrades to a plain editor, never invisible text.
      const surface = document.createElement("div");
      surface.className = "editor-surface";
      const colored = document.createElement("code");
      const mirror = document.createElement("pre");
      mirror.className = "editor-code";
      mirror.setAttribute("aria-hidden", "true");
      mirror.appendChild(colored);

      const ta = document.createElement("textarea");
      ta.value = this.v.source || "";
      ta.spellcheck = false;
      surface.append(mirror, ta);

      const paint = () => {
        if (!surface.classList.contains("highlighted")) return;
        colored.textContent = `${ta.value}\n`;   // trailing NL keeps the last line in step
        docsHtml.highlight.element(colored, "mermaid");
      };
      docsHtml.highlight.ensure().then(() => {
        surface.classList.add("highlighted");
        paint();
      }).catch(() => {});

      ta.addEventListener("scroll", () => {
        mirror.scrollTop = ta.scrollTop;
        mirror.scrollLeft = ta.scrollLeft;
      });
      // Arrow cursor over the scrollbars — CSS can't target ::-webkit-scrollbar.
      ta.addEventListener("pointermove", (e) => {
        const overBar = e.offsetX >= ta.clientWidth || e.offsetY >= ta.clientHeight;
        ta.style.cursor = overBar ? "default" : "";
      });

      const error = document.createElement("p");
      error.className = "editor-error";

      const hint = document.createElement("p");
      hint.className = "editor-hint";
      hint.textContent =
        "Live preview — session only. Copy the source into the document to keep changes.";

      let timer;
      ta.addEventListener("input", () => {
        this.v.source = ta.value;              // the copy button copies what you see
        paint();
        clearTimeout(timer);
        timer = setTimeout(() => this.#rerender(ta.value, error), EDIT_DEBOUNCE);
      });

      // right-edge grip: drag to resize; double-click restores the CSS default
      const grip = document.createElement("div");
      grip.className = "mermaid-editor-resize diagram-exclude";
      grip.title = "drag to resize · double-click to reset";
      docsHtml.util.drag(grip, {
        start: () => ({
          width: panel.getBoundingClientRect().width,
          max: this.v.figure.getBoundingClientRect().width - EDITOR.keepDiagram,
        }),
        move: (s, dx) => {
          panel.style.width =
            `${Math.min(s.max, Math.max(EDITOR.minWidth, s.width + dx))}px`;
        },
      });
      grip.addEventListener("dblclick", () => { panel.style.width = ""; });

      panel.append(surface, error, hint, grip);
      return panel;
    }

    /** Re-render from edited source, PRESERVING the current view — the point is
        editing one region of a large diagram while zoomed into it. On a parse
        error the last good render stays.

        The SVG ELEMENT IS NEVER REPLACED, so the transform (and thus the view)
        survives untouched and nothing flickers. The new render's attributes and
        content are adopted into the existing node; the id must come along
        because the embedded <style> Mermaid emits targets it. */
    async #rerender(text, errorEl) {
      const svg = this.v.svg;
      try {
        await window.mermaid.parse(text);              // validate without touching the DOM
        const { svg: markup } = await window.mermaid.render(
          `mmd-live-${this.v.index}-${++this.seq}`, text);
        errorEl.textContent = "";

        const tpl = document.createElement("template");
        tpl.innerHTML = markup.trim();
        const next = tpl.content.querySelector("svg");
        for (const attr of [...svg.attributes])        // wipe, except the transform
          if (attr.name !== "style") svg.removeAttribute(attr.name);
        for (const attr of [...next.attributes])
          if (attr.name !== "style") svg.setAttribute(attr.name, attr.value);
        svg.innerHTML = next.innerHTML;
      } catch (e) {
        errorEl.textContent = String(e.message || e).split("\n")[0];
      }
    }
  }

  /* --------------------------------------------------------------- feature */

  docsHtml.register({
    name: "diagram-mermaid",
    selector: "pre.mermaid",

    async init(pres) {
      // Stash each source now — mermaid.run replaces the block's content.
      const sources = new Map();
      for (const pre of pres) sources.set(pre, pre.textContent.trim());

      await docsHtml.util.loadScript(MERMAID);
      window.mermaid.initialize({
        startOnLoad: false,
        flowchart: { useMaxWidth: false }, sequence: { useMaxWidth: false },
        er: { useMaxWidth: false }, class: { useMaxWidth: false },
        state: { useMaxWidth: false }, gantt: { useMaxWidth: false },
      });
      await window.mermaid.run({ querySelector: "pre.mermaid" });

      let index = 0;
      for (const pre of pres) {
        const svg = pre.querySelector("svg");
        if (!svg || pre.hasAttribute("data-viewer")) continue;
        pre.setAttribute("data-viewer", "1");

        const viewer = new docsHtml.diagram.Viewer({
          pre, svg, index: ++index,
          source: sources.get(pre) || "",
          copyTitle: "copy Mermaid source",
          extraButtons: [{
            icon: "edit", title: "edit source (live preview)",
            action: (v, btn) => v.editor.toggle(btn),
          }],
        });
        viewer.editor = new SourceEditor(viewer);
      }
    },
  });
})();
