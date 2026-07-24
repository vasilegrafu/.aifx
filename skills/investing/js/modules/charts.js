/* docs-html/charts — the shared chart frame. ENGINE-AGNOSTIC.

   Every chart in the system, whatever renders it, ends up as an <svg> inside
   the same card: the validated surface, a fixed canvas height, an icon toolbar
   (download SVG · copy source), and one debounced resize dispatch for the whole
   page. This file owns all of that and knows nothing about any engine.

   An engine module (today only chart-apache-echarts.js; the pattern takes more)
   does exactly three things: parse its own spec, build a frame, and draw into
   `frame.canvas`.

       const frame = new docsHtml.chart.Frame({ pre, index, source });
       <engine>.renderInto(frame.canvas, spec);
       frame.onResize(() => <engine>.resize());

   `pre` is the source block; it is hidden once the chart renders and stays in
   the DOM as the fallback (charts.css styles it as a readable code box, so an
   unreachable CDN or an invalid spec degrades to source instead of breaking).

   It also owns the DESIGN SYSTEM's chart colour tokens as plain data — PALETTE
   (categorical), RAMP (sequential) and TOKENS (ink, axes, and the semantic
   direction colours) below. They are deliberately NOT in any engine's theme
   format: an engine translates them into whatever shape it needs, so a second
   engine inherits the same colors rather than re-picking them. The VALUES come
   from css/modules/theme.css — rebrand there, never per chart and never per
   engine. */

"use strict";

docsHtml.chart = (() => {
  /* Colours come from the ACTIVE THEME, read once from CSS custom properties.

     An engine's theme object cannot hold `var(--x)` — ECharts wants a literal
     — so the values are resolved here, at init, and handed over already
     substituted. Reading them (rather than hardcoding them, as this file did
     before 4.0.0) is what lets one document render in any theme, and removes
     a duplication that used to be kept in step with base.css by hand.

     ONCE is enough: the palette is fixed for the life of the page, so nothing
     re-reads and nothing re-renders. Retheming means editing theme.css; the
     charts follow on the next load.

     Every read carries the light-theme value as a fallback, so a stylesheet
     that fails to load can never blank a chart. */
  const css = getComputedStyle(document.documentElement);
  const read = (name, fallback) =>
    css.getPropertyValue(name).trim() || fallback;
  const readList = (prefix, fallbacks) =>
    fallbacks.map((f, i) => read(`${prefix}${i + 1}`, f));

  /* The 8-slot categorical palette, in FIXED order (never cycled).

     These are the Okabe-Ito colours — the published reference set for
     categorical colour under colour vision deficiency — with pure black
     replaced by the document's own ink, because a pure-black series in a
     document whose text is #182338 reads as an axis rather than as data.

     Slot order is by CONTRAST against the chart surface, not by separation:
     the first slots are used most, so they are the ones that must be legible.
     The three leading slots clear 3:1 unaided; the set stays separable at
     every prefix length. A theme orders the same eight hues for its OWN
     surface: on a dark ground the order differs, because legibility inverts.

     Do not substitute colours here casually. This set stays separable under
     protanopia, deuteranopia and tritanopia — its worst pair is CIEDE2000
     11.1, which is as good as eight categorical colours get. An ad-hoc
     replacement will not hold that property; take a published reference set. */
  const PALETTE = readList("--chart-palette-",
                           ["#0072b2", "#d55e00", "#009e73", "#cc79a7",
                            "#56b4e9", "#e69f00", "#182338", "#f0e442"]);

  /* Ink, axis and surface tokens, from the active theme.

     positive/negative/caution are SEMANTIC, not categorical — they mirror
     --decision / --risk / --warning. They exist for the one exception to
     "status colours are reserved": direction is not identity. A candlestick's
     up/down and a waterfall's inflow/outflow encode which WAY a number moved,
     not which series it belongs to. Never assign one to a series.

     They are also never the sole encoding — positive/negative fail
     deuteranopia separation by construction (that is what red/green means), so
     any mark using them carries a second cue: hollow vs filled body, a sign in
     the label, or position relative to the axis. */
  const TOKENS = {
    ink:      read("--chart-ink", "#182338"),
    muted:    read("--chart-muted", "#5b6b81"),
    axis:     read("--chart-axis", "#c3c2b7"),
    grid:     read("--chart-grid", "#eef1f5"),
    surface:  read("--chart-surface", "#ffffff"),
    border:   read("--chart-border", "#dde3ea"),
    positive: read("--chart-positive", "#15693b"),
    negative: read("--chart-negative", "#b42331"),
    caution:  read("--chart-caution", "#8a5a00"),
    /* Not themed: the type is the same in every theme. Read from --font-text
       so the engine matches the document rather than restating the stack. */
    font:     read("--font-text",
                   "Inter, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"),
  };

  /* Sequential ramp for CONTINUOUS encodings — heatmap cells, visualMap, any
     ordered quantity. The categorical palette is wrong here: eight unrelated
     hues imply eight categories, and ECharts' stock blue→red default reads as
     good→bad on data that carries no such judgement. Anchored on the theme's
     accent and monotonic in luminance, which is what makes it survive
     greyscale printing and every form of colour vision deficiency. A dark
     theme reverses the direction — low values dark, high values bright — and
     monotonicity is the property it must not lose. */
  const RAMP = readList("--chart-ramp-",
                        ["#eaf1f9", "#c5d9ee", "#9ac0e0",
                         "#6aa3d0", "#3f7fb8", "#1f4e8c"]);

  const DEFAULT_HEIGHT = 340;
  const RESIZE_DEBOUNCE = 150;

  /* One debounced resize dispatch for every chart on the page, whatever engine
     drew them — not one listener per chart. */
  const resizers = [];
  let timer;
  addEventListener("resize", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      for (const fn of resizers) {
        try { fn(); } catch (e) { /* one chart failing must not stop the rest */ }
      }
    }, RESIZE_DEBOUNCE);
  });

  /** One chart's card: the surface, the canvas an engine draws into, and the
      toolbar. */
  class Frame {

    /** The toolbar, declaratively — same three entry kinds as the diagram
        Viewer's spec:
          { sep: true }                    a group separator
          { render: (f) => element }       any custom element
          { icon, title, action }          a button */
    static BUTTONS = [
      { icon: "download", title: "download as SVG", action: (f) => f.downloadSvg() },
      { icon: "copy",     title: null,              action: (f, btn) => f.copySource(btn) },
    ];

    constructor({ pre, index = 1, source = "", copyTitle = "copy chart source",
                  height, extraButtons = [] }) {
      this.pre = pre;
      this.index = index;
      this.source = source;              // live source; engines may update it
      this.copyTitle = copyTitle;
      this.extraButtons = extraButtons;

      // The generated figure is the card; the source <pre> stays in the DOM,
      // hidden, as the degradation path.
      this.figure = document.createElement("figure");
      this.figure.className = "chart-figure";
      pre.after(this.figure);
      pre.hidden = true;

      this.canvas = document.createElement("div");
      this.canvas.className = "chart-canvas";
      // Height is inline because an engine measures the container before it can
      // draw; per-document tuning is data-height on the source block.
      this.canvas.style.height =
        (height ?? docsHtml.data(pre, "height", DEFAULT_HEIGHT)) + "px";
      this.figure.appendChild(this.canvas);

      this.#buildToolbar();
    }

    /** Register a redraw callback with the shared debounced resize dispatch. */
    onResize(fn) { resizers.push(fn); }

    /* ---- export actions ---- */

    /** The <svg> is queried lazily: it does not exist until the engine has
        drawn, and an engine may replace it on redraw. */
    downloadSvg() {
      const svg = this.canvas.querySelector("svg");
      if (!svg) return;
      const clone = svg.cloneNode(true);
      clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
      const blob = new Blob([new XMLSerializer().serializeToString(clone)],
                            { type: "image/svg+xml;charset=utf-8" });
      docsHtml.util.downloadBlob(`chart-${this.index}.svg`, blob);
    }

    copySource(btn) {
      docsHtml.util.copyText(this.source || "").then(() => {
        btn.innerHTML = docsHtml.icons.check;     // brief "done" flash
        setTimeout(() => { btn.innerHTML = docsHtml.icons.copy; }, 1200);
      }).catch(() => {});
    }

    /* ---- private wiring ---- */

    /** Build the toolbar by walking the spec — generic, knows no single entry.
        It hangs off the figure, not the canvas: the canvas belongs to the
        engine, which is free to replace its contents on every redraw. */
    #buildToolbar() {
      const bar = document.createElement("div");
      bar.className = "chart-tools";

      const specs = this.extraButtons.length
        ? [...this.extraButtons, { sep: true }, ...Frame.BUTTONS]
        : [...Frame.BUTTONS];

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
      this.figure.appendChild(bar);
    }
  }

  /** Flag an unparseable spec: the source stays visible, styled as an error. */
  const markError = (pre) => pre.classList.add("chart-error");

  /* A chart spec sometimes has to NAME a design colour — a preset colouring
     sankey nodes by role, or a markLine drawn in the caution tone. Writing the
     hex would fork the palette into every document and defeat the one-place
     rebrand, so a spec references it instead:

         "palette:3"       the 3rd categorical slot (counts from 1)
         "token:positive"  any TOKENS colour
         "ramp:2"          the 2nd step of the sequential ramp

     resolveColors walks a parsed spec and substitutes the real values. It lives
     here, not in an engine: naming a design colour is a design-system concern,
     so every engine resolves the same references. Unknown names are left as
     written — an engine ignoring a colour it cannot read beats a chart that
     throws. */
  const COLOR_REF = /^(palette|token|ramp):(.+)$/;

  const resolveColor = (text) => {
    const m = COLOR_REF.exec(text);
    if (!m) return text;
    const [, kind, key] = m;
    if (kind === "token") return TOKENS[key] ?? text;
    const list = kind === "palette" ? PALETTE : RAMP;
    const i = Number(key);
    return Number.isInteger(i) && i >= 1 && i <= list.length ? list[i - 1] : text;
  };

  /** Substitute every colour reference in a parsed spec, in place. */
  const resolveColors = (node) => {
    if (Array.isArray(node)) {
      node.forEach((v, i) => {
        if (typeof v === "string") node[i] = resolveColor(v);
        else if (v && typeof v === "object") resolveColors(v);
      });
    } else if (node && typeof node === "object") {
      for (const k of Object.keys(node)) {
        const v = node[k];
        if (typeof v === "string") node[k] = resolveColor(v);
        else if (v && typeof v === "object") resolveColors(v);
      }
    }
    return node;
  };

  return { PALETTE, TOKENS, RAMP, Frame, markError, resolveColors, DEFAULT_HEIGHT };
})();
