/* docs-html/util — leaf helpers. No DOM state, no knowledge of any feature.
   Everything here is a small, generic capability a feature may borrow. */

"use strict";

docsHtml.util = (() => {
  /** src → Promise. Engines load once no matter how many features ask. */
  const scripts = new Map();

  return {

  /** Load a classic script from a URL (the CDN engines); resolves on load.
      Deduplicated: repeated calls for the same URL share one load. */
  loadScript(src) {
    if (!scripts.has(src))
      scripts.set(src, new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = src;
        s.async = true;
        s.onload = resolve;
        s.onerror = () => reject(new Error(`failed to load ${src}`));
        document.head.appendChild(s);
      }));
    return scripts.get(src);
  },

  /** Copy text to the clipboard; falls back for non-secure contexts. */
  copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText)
      return navigator.clipboard.writeText(text);
    return new Promise((resolve, reject) => {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy") ? resolve() : reject(new Error("copy failed"));
      } catch (e) {
        reject(e);
      } finally {
        ta.remove();
      }
    });
  },

  /** Wire a drag interaction on a handle element: pointer capture, a
      .dragging class while active, and clean listener removal.
      `spec.start()` captures state at pointerdown; `spec.move(state, dx, dy)`
      receives it with the pointer's delta from the drag origin. */
  drag(handle, spec) {
    handle.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      handle.setPointerCapture(e.pointerId);
      handle.classList.add("dragging");
      const state = spec.start();
      const move = (ev) => spec.move(state, ev.clientX - e.clientX, ev.clientY - e.clientY);
      const up = () => {
        handle.classList.remove("dragging");
        handle.removeEventListener("pointermove", move);
        handle.removeEventListener("pointerup", up);
      };
      handle.addEventListener("pointermove", move);
      handle.addEventListener("pointerup", up);
    });
  },

  /** Offer a Blob as a named download. */
  downloadBlob(filename, blob) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  },

  };
})();
