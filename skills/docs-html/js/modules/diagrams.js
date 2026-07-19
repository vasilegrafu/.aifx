/* docs-html/diagrams — everything diagrams: renders each <pre class="mermaid">
   with Mermaid, then gives it a pan/zoom viewport with an icon toolbar.
   One feature, one file: the CDN pins, the source stash, the DiagramViewer
   class, and the feature registration all live here.

   The engines load from CDN only when the document actually contains a
   diagram (the feature is dormant otherwise — see core.js). If the CDN is
   unreachable, diagrams.css leaves the Mermaid source visible as a readable
   code box: the page still works. */

"use strict";

(() => {
  const MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js";
  const PANZOOM = "https://cdn.jsdelivr.net/npm/@panzoom/panzoom@4.6.0/dist/panzoom.min.js";

  const ZOOM = { min: 0.4, max: 6, step: 0.25 };
  const FIT_PAD = 0.95;                 // fit leaves a little breathing room
  const VIEW = { maxShare: 0.7, minHeight: 96 };  // default cap 70vh; resize floor px
  const EDIT_DEBOUNCE = 400;            // ms of typing pause before re-render
  const EDITOR = { minWidth: 256, keepDiagram: 160 };  // panel resize clamps, px

  /** Mermaid source per diagram, stashed before render (render replaces it). */
  const sources = new WeakMap();

  /* ---------------------------------------------------------------- viewer */

  /** One rendered diagram: owns its Panzoom instance, toolbar, and state. */
  class DiagramViewer {

    /** The toolbar, declaratively. Three kinds of entry — the builder knows
        nothing about any particular button, so changing the toolbar is ONLY
        editing this list:
          { sep: true }                          a group separator
          { render: (v) => element }             any custom element
          { icon, title, action, wire? }         a button; `wire` is an optional
                                                 one-time setup hook for
                                                 stateful buttons */
    static BUTTONS = [
      { icon: "zoomOut",    title: "zoom out",             action: (v) => v.zoomOut() },
      { render: (v) => v.buildZoomLabel() },
      { icon: "zoomIn",     title: "zoom in",              action: (v) => v.zoomIn() },
      { sep: true },
      { icon: "fit",        title: "fit diagram to view",  action: (v) => v.fit() },
      { icon: "reset",      title: "reset to 100%",        action: (v) => v.reset() },
      { sep: true },
      { icon: "fullscreen", title: "fullscreen",
        action: (v) => v.toggleFullscreen(),
        wire:   (v, btn) => v.trackFullscreen(btn) },
      { sep: true },
      { icon: "edit",       title: "edit source (live preview)",
        action: (v, btn) => v.toggleEditor(btn) },
      { sep: true },
      { icon: "download",   title: "download as SVG",      action: (v) => v.downloadSvg() },
      { icon: "copy",       title: "copy Mermaid source",  action: (v, btn) => v.copySource(btn) },
    ];

    constructor(pre, index) {
      this.pre = pre;
      this.index = index;
      this.svg = pre.querySelector("svg");
      // The canvas: a permanent wrapper around the SVG. It is the diagram
      // pane of the flex row (the editor panel sits BESIDE it, never over
      // it), the clip box for panning, and — via Panzoom's canvas:true, which
      // binds to the SVG's parent — the exact pan/zoom event surface.
      this.canvas = document.createElement("div");
      this.canvas.className = "mermaid-canvas";
      this.svg.replaceWith(this.canvas);
      this.canvas.appendChild(this.svg);
      // Per-document tuning via data- attributes on the diagram's own markup,
      // e.g. <pre class="mermaid" data-max-scale="10"> — never per-document JS.
      this.zoom = {
        min: docsHtml.data(pre, "min-scale", ZOOM.min),
        max: docsHtml.data(pre, "max-scale", ZOOM.max),
      };
      this.renderSeq = 0;               // unique ids for live re-renders
      this.editor = null;               // the source panel, when open
      this.#bindPanzoom();
      this.#setDefaultHeight();
      this.#wireWheel();
      this.#buildToolbar();
      this.#buildResizeHandle();
    }

    /* ---- zoom / view actions ---- */

    zoomIn()  { this.pz.zoomIn(); }
    zoomOut() { this.pz.zoomOut(); }
    reset()   { this.pz.reset(); }

    /** Scale + center the whole diagram inside the viewport box. */
    fit() {
      // The SVG's on-screen rect scales with the transform, so its unscaled
      // size is rect / current scale; fit = the scale at which that fills the box.
      const rect = this.svg.getBoundingClientRect();
      const scale = this.pz.getScale();
      const baseW = rect.width / scale, baseH = rect.height / scale;
      const box = this.pre.getBoundingClientRect();
      let s = Math.min(box.width / baseW, box.height / baseH) * FIT_PAD;
      s = Math.max(this.zoom.min, Math.min(this.zoom.max, s));
      this.pz.zoom(s, { animate: false });
      // Panzoom's transform is scale() then translate(), origin 0 0 — a pan of
      // x moves the diagram x*s pixels on screen, so divide the offset by s.
      this.pz.pan((box.width - baseW * s) / 2 / s,
                  (box.height - baseH * s) / 2 / s, { animate: false });
    }

    toggleFullscreen() {
      if (document.fullscreenElement === this.pre) document.exitFullscreen();
      else this.pre.requestFullscreen();
    }

    /* ---- export actions ---- */

    downloadSvg() {
      const clone = this.svg.cloneNode(true);
      clone.removeAttribute("style");         // drop the pan/zoom transform
      clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
      const blob = new Blob([new XMLSerializer().serializeToString(clone)],
                            { type: "image/svg+xml;charset=utf-8" });
      docsHtml.util.downloadBlob(`diagram-${this.index}.svg`, blob);
    }

    copySource(btn) {
      docsHtml.util.copyText(sources.get(this.pre) || "").then(() => {
        btn.innerHTML = docsHtml.icons.check;              // brief "done" flash
        setTimeout(() => { btn.innerHTML = docsHtml.icons.copy; }, 1200);
      }).catch(() => {});
    }

    /* ---- toolbar parts (referenced by the BUTTONS spec) ---- */

    /** The live zoom-% readout, updated from Panzoom's change event. */
    buildZoomLabel() {
      this.label = document.createElement("span");
      this.label.className = "zoom-label";
      this.label.textContent = "100%";
      this.#bindZoomLabel();
      return this.label;
    }

    /** Keep the fullscreen button's pressed state true even when Esc exits. */
    trackFullscreen(btn) {
      btn.setAttribute("aria-pressed", "false");
      document.addEventListener("fullscreenchange", () => {
        btn.setAttribute("aria-pressed", String(document.fullscreenElement === this.pre));
      });
    }

    /* ---- source editor: ✎ splits the viewport, source left / diagram right ---- */

    toggleEditor(btn) {
      if (this.editor) {
        this.editor.remove();
        this.editor = null;
        this.pre.classList.remove("editing");
        btn.setAttribute("aria-pressed", "false");
        return;
      }
      this.editor = this.#buildEditor();
      this.pre.insertBefore(this.editor, this.canvas);   // side panel, left of the canvas
      this.pre.classList.add("editing");
      btn.setAttribute("aria-pressed", "true");
      this.editor.querySelector("textarea").focus();
    }

    #buildEditor() {
      const panel = document.createElement("div");
      // panzoom-exclude: typing and selecting in the panel must never pan.
      panel.className = "mermaid-editor panzoom-exclude";

      // The editing surface is an overlay: a Prism-colored <pre><code> behind
      // a transparent-text textarea with identical metrics — native caret,
      // selection, and undo, with syntax coloring underneath. The transparent
      // text switches on only once Prism has actually loaded (.highlighted),
      // so an unreachable CDN degrades to a plain editor, never invisible text.
      const surface = document.createElement("div");
      surface.className = "editor-surface";
      const colored = document.createElement("code");
      const mirror = document.createElement("pre");
      mirror.className = "editor-code";
      mirror.setAttribute("aria-hidden", "true");
      mirror.appendChild(colored);

      const ta = document.createElement("textarea");
      ta.value = sources.get(this.pre) || "";
      ta.spellcheck = false;
      surface.append(mirror, ta);

      const paint = () => {
        if (!surface.classList.contains("highlighted")) return;
        // trailing newline keeps the mirror's last line in step while typing
        colored.textContent = `${ta.value}\n`;
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
      // Arrow cursor over the scrollbars (the strip beyond client width/height)
      // — CSS can't set a cursor on ::-webkit-scrollbar, so flip it here.
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
        sources.set(this.pre, ta.value);   // the copy button copies what you see
        paint();
        clearTimeout(timer);
        timer = setTimeout(() => this.#rerender(ta.value, error), EDIT_DEBOUNCE);
      });

      // right-edge grip: drag to resize the panel; double-click restores the
      // stylesheet default width (325px)
      const grip = document.createElement("div");
      grip.className = "mermaid-editor-resize";
      grip.title = "drag to resize · double-click to reset";
      docsHtml.util.drag(grip, {
        start: () => ({
          width: panel.getBoundingClientRect().width,
          max: this.pre.getBoundingClientRect().width - EDITOR.keepDiagram,
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

    /** Re-render the diagram from edited source, PRESERVING the current view —
        the whole point is editing one small region of a large diagram while
        zoomed into it. On a parse error the last good render stays.

        The SVG ELEMENT IS NEVER REPLACED: Panzoom stays bound and the
        transform stays untouched, so the view survives trivially and nothing
        flickers (destroy/recreate painted wrong-transform frames — Panzoom
        applies start options asynchronously). The new render's attributes and
        content are adopted into the existing node; the id must come along
        because the embedded <style> mermaid emits targets it. */
    async #rerender(text, errorEl) {
      try {
        await window.mermaid.parse(text);          // validate without touching the DOM
        const { svg: markup } = await window.mermaid.render(
          `mmd-live-${this.index}-${++this.renderSeq}`, text);
        errorEl.textContent = "";

        const tpl = document.createElement("template");
        tpl.innerHTML = markup.trim();
        const next = tpl.content.querySelector("svg");
        for (const attr of [...this.svg.attributes])       // wipe, except the
          if (attr.name !== "style") this.svg.removeAttribute(attr.name);   // transform Panzoom owns
        for (const attr of [...next.attributes])
          if (attr.name !== "style") this.svg.setAttribute(attr.name, attr.value);
        this.svg.innerHTML = next.innerHTML;
      } catch (e) {
        errorEl.textContent = String(e.message || e).split("\n")[0];
      }
    }

    /* ---- private wiring ---- */

    /** Attach Panzoom to the SVG. Bound once — live re-renders reuse the same
        SVG element (see #rerender), so this never runs again. */
    #bindPanzoom() {
      this.pz = window.Panzoom(this.svg, {
        minScale: this.zoom.min, maxScale: this.zoom.max, step: ZOOM.step,
        canvas: true, cursor: "grab",
      });
    }

    /** Point the zoom-% label at the current SVG's Panzoom events. */
    #bindZoomLabel() {
      this.svg.addEventListener("panzoomchange", (e) => {
        this.label.textContent = `${Math.round(e.detail.scale * 100)}%`;
      });
    }

    /** The viewport's default height: the diagram's natural height, capped at
        70% of the window. Set inline (not via CSS max-height) so the resize
        handle can grow the box past the cap. */
    #setDefaultHeight() {
      const natural = Math.ceil(this.svg.getBoundingClientRect().height) + 2;
      this.pre.style.height =
        `${Math.max(VIEW.minHeight, Math.min(natural, window.innerHeight * VIEW.maxShare))}px`;
    }

    /** The bottom-edge grip: drag vertically to resize the viewport;
        double-click to restore the default height. */
    #buildResizeHandle() {
      const handle = document.createElement("div");
      // panzoom-exclude: dragging the handle must resize, never pan.
      handle.className = "mermaid-resize panzoom-exclude";
      handle.title = "drag to resize · double-click to reset";

      docsHtml.util.drag(handle, {
        start: () => this.pre.getBoundingClientRect().height,
        move: (startH, _dx, dy) => {
          this.pre.style.height = `${Math.max(VIEW.minHeight, startH + dy)}px`;
        },
      });
      handle.addEventListener("dblclick", () => this.#setDefaultHeight());

      this.pre.appendChild(handle);
    }

    /** Ctrl+wheel zooms the diagram; a plain wheel keeps scrolling the page.
        On the canvas, not the pre — the pointer must be over the diagram. */
    #wireWheel() {
      this.canvas.addEventListener("wheel", (e) => {
        if (!e.ctrlKey) return;
        e.preventDefault();
        this.pz.zoomWithWheel(e);
      }, { passive: false });
    }

    /** Build the toolbar chip by walking the BUTTONS spec. Fully generic — no
        knowledge of any particular entry lives here. */
    #buildToolbar() {
      const bar = document.createElement("div");
      // panzoom-exclude: Panzoom's built-in excludeClass — pointerdown on the
      // toolbar must click its buttons, not start a pan of the diagram.
      bar.className = "mermaid-tools panzoom-exclude";

      for (const spec of DiagramViewer.BUTTONS) {
        if (spec.sep) {
          const s = document.createElement("span");
          s.className = "sep";
          bar.appendChild(s);
        } else if (spec.render) {
          bar.appendChild(spec.render(this));
        } else {
          const b = document.createElement("button");
          b.type = "button";
          b.title = spec.title;
          b.setAttribute("aria-label", spec.title);
          b.innerHTML = docsHtml.icons[spec.icon];
          b.addEventListener("click", () => spec.action(this, b));
          if (spec.wire) spec.wire(this, b);
          bar.appendChild(b);
        }
      }
      this.canvas.appendChild(bar);   // top-right of the diagram pane, never over the editor
    }
  }

  /* --------------------------------------------------------------- feature */

  docsHtml.register({
    name: "diagrams",
    selector: "pre.mermaid",

    async init(pres) {
      // Stash each diagram's source now — mermaid.run replaces the content.
      for (const pre of pres) sources.set(pre, pre.textContent.trim());

      await docsHtml.util.loadScript(MERMAID);
      window.mermaid.initialize({
        startOnLoad: false,
        flowchart: { useMaxWidth: false }, sequence: { useMaxWidth: false },
        er: { useMaxWidth: false }, class: { useMaxWidth: false },
        state: { useMaxWidth: false }, gantt: { useMaxWidth: false },
      });
      await window.mermaid.run({ querySelector: "pre.mermaid" });

      await docsHtml.util.loadScript(PANZOOM);
      const done = document.querySelectorAll("pre.mermaid[data-processed='true']");
      let index = 0;
      for (const pre of done) {
        if (pre.getAttribute("data-pz") || !pre.querySelector("svg")) continue;
        pre.setAttribute("data-pz", "1");
        new DiagramViewer(pre, ++index);
      }
    },
  });
})();
