/* docs-html/diagrams — the shared diagram viewport. ENGINE-AGNOSTIC.

   Every diagram in the system, whatever renders it, ends up as an <svg> shown
   in the same bounded viewport: pan by dragging, Ctrl+wheel to zoom, and one
   icon toolbar (zoom % · fit · reset · fullscreen · download SVG · copy source).
   This file owns all of that and knows nothing about Mermaid or draw.io.

   The engine modules (diagram-mermaid.js, diagram-drawio.js) do exactly two
   things: turn their source into an <svg>, then hand it here.

       new docsHtml.diagram.Viewer({ pre, svg, index, source, copyTitle,
                                     extraButtons })

   `pre` is the source block; it is hidden once the diagram renders and stays in
   the DOM as the fallback (each engine's CSS styles it as a readable code box,
   so an unreachable CDN degrades to source instead of breaking).
   `extraButtons` lets an engine add its own tools — Mermaid's ✎ source editor.

   Pan/zoom is a small self-contained transform, deliberately NOT an external
   pan library: the diagrams.net bundle ships its own global `Panzoom` that
   clobbers @panzoom, so owning this removes both a dependency and a load race. */

"use strict";

docsHtml.diagram = (() => {
  const ZOOM = { min: 0.4, max: 8, stepBtn: 1.25, stepWheel: 1.1 };
  const FIT_PAD = 0.95;                            // fit leaves a little breathing room
  const VIEW = { maxShare: 0.7, minHeight: 96 };   // default height cap 70vh; resize floor px

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

  /** One rendered diagram: its viewport, transform state, and toolbar. */
  class Viewer {

    /** The toolbar, declaratively. Three kinds of entry:
          { sep: true }                    a group separator
          { render: (v) => element }       any custom element
          { icon, title, action, wire? }   a button; `wire` is a one-time hook
                                           for stateful buttons */
    static BUTTONS = [
      { icon: "zoomOut",    title: "zoom out",  action: (v) => v.zoomBy(1 / ZOOM.stepBtn) },
      { render: (v) => v.buildZoomLabel() },
      { icon: "zoomIn",     title: "zoom in",   action: (v) => v.zoomBy(ZOOM.stepBtn) },
      { sep: true },
      { icon: "fit",        title: "fit diagram to view", action: (v) => v.fit() },
      { icon: "reset",      title: "reset to 100%",       action: (v) => v.reset() },
      { sep: true },
      { icon: "fullscreen", title: "fullscreen",
        action: (v) => v.toggleFullscreen(),
        wire:   (v, btn) => v.trackFullscreen(btn) },
    ];

    static EXPORT_BUTTONS = [
      { icon: "download", title: "download as SVG", action: (v) => v.downloadSvg() },
      { icon: "copy",     title: null,              action: (v, btn) => v.copySource(btn) },
    ];

    constructor({ pre, svg, index = 1, source = "", copyTitle = "copy source",
                  extraButtons = [] }) {
      this.pre = pre;
      this.svg = svg;
      this.index = index;
      this.source = source;                  // live source; engines may update it
      this.copyTitle = copyTitle;
      this.extraButtons = extraButtons;
      this.scale = 1; this.x = 0; this.y = 0;

      // Unified container: a generated figure is the viewport; the source <pre>
      // stays in the DOM, hidden, as the degradation path.
      this.figure = document.createElement("figure");
      this.figure.className = "diagram-figure";
      pre.after(this.figure);
      pre.hidden = true;

      this.canvas = document.createElement("div");
      this.canvas.className = "diagram-canvas";
      this.figure.appendChild(this.canvas);
      this.canvas.appendChild(svg);

      this.#setDefaultHeight();
      this.#wireDrag();
      this.#wireWheel();
      this.#buildToolbar();
      this.#buildResizeHandle();
      this.apply();
    }

    /* ---- view actions ---- */

    zoomBy(factor) { this.scale = clamp(this.scale * factor, ZOOM.min, ZOOM.max); this.apply(); }

    /** 100%: the engine's own natural presentation (Mermaid natural px,
        draw.io fit-to-column-width via its viewBox). */
    reset() { this.scale = 1; this.x = 0; this.y = 0; this.apply(); }

    /** Scale + centre the whole diagram inside the current viewport box. */
    fit() {
      const rect = this.svg.getBoundingClientRect();
      const baseW = rect.width / this.scale, baseH = rect.height / this.scale;
      if (!baseW || !baseH) return;
      const box = this.figure.getBoundingClientRect();
      const s = clamp(Math.min(box.width / baseW, box.height / baseH) * FIT_PAD,
                      ZOOM.min, ZOOM.max);
      this.scale = s;
      // transform is `translate() scale()` with origin 0 0 — the translate is in
      // unscaled parent pixels, so no dividing by the scale.
      this.x = (box.width - baseW * s) / 2;
      this.y = (box.height - baseH * s) / 2;
      this.apply();
    }

    toggleFullscreen() {
      if (document.fullscreenElement === this.figure) document.exitFullscreen();
      else this.figure.requestFullscreen();
    }

    /* ---- export actions ---- */

    downloadSvg() {
      const clone = this.svg.cloneNode(true);
      clone.removeAttribute("style");             // drop the pan/zoom transform
      clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
      const blob = new Blob([new XMLSerializer().serializeToString(clone)],
                            { type: "image/svg+xml;charset=utf-8" });
      docsHtml.util.downloadBlob(`diagram-${this.index}.svg`, blob);
    }

    copySource(btn) {
      docsHtml.util.copyText(this.source || "").then(() => {
        btn.innerHTML = docsHtml.icons.check;     // brief "done" flash
        setTimeout(() => { btn.innerHTML = docsHtml.icons.copy; }, 1200);
      }).catch(() => {});
    }

    /* ---- toolbar parts (referenced by the BUTTONS spec) ---- */

    buildZoomLabel() {
      this.label = document.createElement("span");
      this.label.className = "zoom-label";
      this.label.textContent = "100%";
      return this.label;
    }

    trackFullscreen(btn) {
      btn.setAttribute("aria-pressed", "false");
      document.addEventListener("fullscreenchange", () => {
        btn.setAttribute("aria-pressed", String(document.fullscreenElement === this.figure));
      });
    }

    /** Write the transform + zoom readout. Public: an engine that re-renders
        into the same SVG (Mermaid's live editor) keeps the view by calling it. */
    apply() {
      this.svg.style.transform = `translate(${this.x}px, ${this.y}px) scale(${this.scale})`;
      if (this.label) this.label.textContent = `${Math.round(this.scale * 100)}%`;
    }

    /** The viewport's default height: the diagram's natural rendered height,
        capped at 70% of the window. Inline (not CSS max-height) so the resize
        grip can grow the box past the cap. */
    setDefaultHeight() { this.#setDefaultHeight(); }

    /* ---- private wiring ---- */

    #setDefaultHeight() {
      const natural = Math.ceil(this.svg.getBoundingClientRect().height) + 2;
      this.figure.style.height =
        `${Math.max(VIEW.minHeight, Math.min(natural, window.innerHeight * VIEW.maxShare))}px`;
    }

    /** Drag the diagram to pan. Anything marked .diagram-exclude (toolbar,
        resize grips, an engine's editor panel) must never start a pan. */
    #wireDrag() {
      let start = null;
      this.canvas.addEventListener("pointerdown", (e) => {
        if (e.target.closest(".diagram-exclude")) return;
        e.preventDefault();
        // Capture keeps the drag alive past the canvas edge; if the pointer
        // isn't capturable the drag must still work, so never let it throw.
        try { this.canvas.setPointerCapture(e.pointerId); } catch (err) { /* non-fatal */ }
        this.canvas.classList.add("grabbing");
        start = { px: e.clientX, py: e.clientY, x: this.x, y: this.y };
      });
      this.canvas.addEventListener("pointermove", (e) => {
        if (!start) return;
        this.x = start.x + (e.clientX - start.px);
        this.y = start.y + (e.clientY - start.py);
        this.apply();
      });
      const end = () => { start = null; this.canvas.classList.remove("grabbing"); };
      this.canvas.addEventListener("pointerup", end);
      this.canvas.addEventListener("pointercancel", end);
    }

    /** Ctrl+wheel zooms the diagram; a plain wheel keeps scrolling the page. */
    #wireWheel() {
      this.canvas.addEventListener("wheel", (e) => {
        if (!e.ctrlKey) return;
        e.preventDefault();
        this.zoomBy(e.deltaY < 0 ? ZOOM.stepWheel : 1 / ZOOM.stepWheel);
      }, { passive: false });
    }

    /** Build the toolbar by walking the spec — generic, knows no single entry. */
    #buildToolbar() {
      const bar = document.createElement("div");
      bar.className = "diagram-tools diagram-exclude";

      const specs = [...Viewer.BUTTONS];
      if (this.extraButtons.length) specs.push({ sep: true }, ...this.extraButtons);
      specs.push({ sep: true }, ...Viewer.EXPORT_BUTTONS);

      for (const spec of specs) {
        if (spec.sep) {
          const s = document.createElement("span");
          s.className = "sep";
          bar.appendChild(s);
        } else if (spec.render) {
          bar.appendChild(spec.render(this));
        } else {
          const b = document.createElement("button");
          b.type = "button";
          const title = spec.title || this.copyTitle;   // copy's label is per-engine
          b.title = title;
          b.setAttribute("aria-label", title);
          b.innerHTML = docsHtml.icons[spec.icon];
          b.addEventListener("click", () => spec.action(this, b));
          if (spec.wire) spec.wire(this, b);
          bar.appendChild(b);
        }
      }
      this.canvas.appendChild(bar);
    }

    /** Bottom-edge grip: drag to resize the viewport, double-click to restore. */
    #buildResizeHandle() {
      const handle = document.createElement("div");
      handle.className = "diagram-resize diagram-exclude";
      handle.title = "drag to resize · double-click to reset";
      docsHtml.util.drag(handle, {
        start: () => this.figure.getBoundingClientRect().height,
        move: (startH, _dx, dy) => {
          this.figure.style.height = `${Math.max(VIEW.minHeight, startH + dy)}px`;
        },
      });
      handle.addEventListener("dblclick", () => this.#setDefaultHeight());
      this.figure.appendChild(handle);
    }
  }

  return { Viewer, ZOOM, VIEW, FIT_PAD };
})();
