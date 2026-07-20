/* docs-html/chart — declarative charts rendered at view time by Apache ECharts.

   Markup (a JSON ECharts `option` as plain text in the document — no images,
   no per-document JS):
     <pre class="chart">{ "xAxis": {...}, "series": [...] }</pre>

   ECharts loads from the pinned CDN only when the document actually contains a
   .chart element, and renders SVG (crisp in print, one <main> column). If the
   CDN is unreachable — or the JSON is invalid — the spec stays visible as a
   readable code box (styled by chart.css); the page never breaks.

   The palette is the design system's validated categorical theme (light
   surface); see css/REFERENCE.md. Everything textual wears the ink tokens, so
   identity is carried by the mark, never by colored text. */

"use strict";

(() => {
  const ECHARTS = "https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js";

  // docs-html ECharts theme — literal token values (ECharts can't read CSS
  // vars). Colors: the validated 8-slot categorical palette in fixed order
  // (never cycled). Ink/axis/grid: base.css tokens. Kept in sync with
  // css/modules/base.css and the dataviz reference palette.
  const INK = "#182338", MUTED = "#5b6b81", AXIS = "#c3c2b7",
        GRID = "#eef1f5", SURFACE = "#ffffff", BORDER = "#dde3ea";
  const FONT = "Inter, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";
  const AXIS_COMMON = {
    axisLine: { lineStyle: { color: AXIS } },
    axisTick: { show: false },
    axisLabel: { color: MUTED },
    splitLine: { lineStyle: { color: GRID } },
  };
  const THEME = {
    color: ["#2a78d6", "#008300", "#e87ba4", "#eda100",
            "#1baf7a", "#eb6834", "#4a3aa7", "#e34948"],
    backgroundColor: "transparent",
    textStyle: { fontFamily: FONT, color: INK },
    title: {
      textStyle: { color: INK, fontWeight: 700, fontSize: 15 },
      subtextStyle: { color: MUTED },
    },
    legend: { textStyle: { color: MUTED }, icon: "roundRect", itemWidth: 14, itemHeight: 8 },
    tooltip: {
      backgroundColor: SURFACE, borderColor: BORDER, borderWidth: 1,
      textStyle: { color: INK, fontFamily: FONT },
      axisPointer: { lineStyle: { color: AXIS }, crossStyle: { color: AXIS } },
    },
    grid: { containLabel: true, left: 8, right: 16, top: 44, bottom: 8 },
    categoryAxis: { ...AXIS_COMMON, splitLine: { show: false } },
    valueAxis: { ...AXIS_COMMON, axisLine: { show: false } },
    logAxis: { ...AXIS_COMMON, axisLine: { show: false } },
    timeAxis: AXIS_COMMON,
    line: { lineStyle: { width: 2 }, symbol: "circle", symbolSize: 8 },
    bar: { itemStyle: { borderRadius: [4, 4, 0, 0] }, barMaxWidth: 44 },
  };

  docsHtml.register({
    name: "chart",
    selector: "pre.chart",

    init(nodes) {
      // Parse every spec FIRST — a bad JSON degrades to source without pulling
      // the ~900 KB engine, and an all-invalid page skips the load entirely.
      const jobs = [];
      for (const pre of nodes) {
        try {
          jobs.push({ pre, option: JSON.parse(pre.textContent) });
        } catch (e) {
          pre.classList.add("chart-error");   // stays visible; source is the fallback
        }
      }
      if (!jobs.length) return;

      docsHtml.util.loadScript(ECHARTS).then(() => {
        window.echarts.registerTheme("docs-html", THEME);
        const charts = [];

        for (const { pre, option } of jobs) {
          const box = document.createElement("figure");
          box.className = "chart-figure";
          const canvas = document.createElement("div");
          canvas.className = "chart-canvas";
          canvas.style.height = docsHtml.data(pre, "height", 340) + "px";
          box.appendChild(canvas);
          pre.after(box);
          pre.hidden = true;   // source kept in the DOM (copy/debug), hidden once drawn

          // Nudge every chart toward the accessible defaults the dataviz method
          // requires, without overriding an author who set them explicitly.
          if (option.aria === undefined) option.aria = { enabled: true };
          if (option.tooltip === undefined) option.tooltip = {};
          if (option.legend === undefined && Array.isArray(option.series)
              && option.series.length > 1) option.legend = {};

          const chart = window.echarts.init(canvas, "docs-html", { renderer: "svg" });
          chart.setOption(option);
          charts.push(chart);
        }

        // Reflow on width change (responsive labels/layout, still crisp SVG).
        let timer;
        addEventListener("resize", () => {
          clearTimeout(timer);
          timer = setTimeout(() => charts.forEach((c) => c.resize()), 150);
        });
      }).catch(() => {});   // CDN down → the JSON spec stays visible, readable
    },
  });
})();
