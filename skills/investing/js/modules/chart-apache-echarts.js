/* docs-html/chart-apache-echarts — declarative charts rendered at view time by
   Apache ECharts. ONE engine behind the shared chart frame (charts.js).

   Markup (a JSON ECharts `option` as plain text in the document — no images,
   no per-document JS):
     <pre class="chart apache-echarts">{ "xAxis": {...}, "series": [...] }</pre>

   `chart` is the marker every engine shares (charts.css styles the fallback
   box once); `apache-echarts` selects this engine.

   ECharts loads from the pinned CDN only when the document actually contains a
   chart of this kind, and renders SVG (crisp in print, one <main> column). If
   the CDN is unreachable — or the JSON is invalid — the spec stays visible as a
   readable code box; the page never breaks.

   The theme below is a TRANSLATION of the design system's chart tokens
   (docsHtml.chart.PALETTE / .TOKENS) into ECharts' theme shape. Change the
   colors in charts.js, never here and never per chart. */

"use strict";

(() => {
  const ECHARTS = "https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js";
  const THEME_NAME = "docs-html";

  /** Translate the shared tokens into an ECharts theme. Built lazily so the
      shared module is guaranteed to have loaded first. */
  const buildTheme = () => {
    const { ink, muted, axis, grid, surface, border, font,
            positive, negative } = docsHtml.chart.TOKENS;
    const { PALETTE, RAMP } = docsHtml.chart;
    const axisCommon = {
      axisLine:  { lineStyle: { color: axis } },
      axisTick:  { show: false },
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: grid } },
    };
    return {
      color: PALETTE,                      // fixed order, never cycled
      backgroundColor: "transparent",
      textStyle: { fontFamily: font, color: ink },
      title: {
        textStyle: { color: ink, fontWeight: 700, fontSize: 15 },
        subtextStyle: { color: muted },
      },
      legend: { textStyle: { color: muted }, icon: "roundRect", itemWidth: 14, itemHeight: 8 },
      tooltip: {
        backgroundColor: surface, borderColor: border, borderWidth: 1,
        textStyle: { color: ink, fontFamily: font },
        axisPointer: { lineStyle: { color: axis }, crossStyle: { color: axis } },
      },
      grid: { containLabel: true, left: 8, right: 16, top: 44, bottom: 8 },
      categoryAxis: { ...axisCommon, splitLine: { show: false } },
      valueAxis:    { ...axisCommon, axisLine: { show: false } },
      logAxis:      { ...axisCommon, axisLine: { show: false } },
      timeAxis:     axisCommon,

      /* Every series type the engine can reach gets a definition. A type left
         out does not fall back to the palette — it falls back to ECharts' stock
         colours, which collide with the reserved status hues and read as
         good/bad on data that carries no judgement. */
      line:    { lineStyle: { width: 2 }, symbol: "circle", symbolSize: 8 },
      bar:     { itemStyle: { borderRadius: [4, 4, 0, 0] }, barMaxWidth: 44 },
      pie:     { itemStyle: { borderColor: surface, borderWidth: 2 },
                 label: { color: ink }, labelLine: { lineStyle: { color: axis } } },
      scatter: { symbolSize: 10, itemStyle: { opacity: .85 } },
      radar:   { lineStyle: { width: 2 }, symbolSize: 6 },
      boxplot: { itemStyle: { borderWidth: 1.5, color: surface },
                 emphasis: { itemStyle: { borderWidth: 2 } } },
      graph:   { lineStyle: { color: axis }, label: { color: ink } },
      funnel:  { itemStyle: { borderColor: surface, borderWidth: 2 },
                 label: { color: ink } },

      /* Candlestick is the documented exception to "status colours are
         reserved": up/down is direction, not series identity. The body is
         HOLLOW when up and FILLED when down, so the reading survives without
         colour — which matters, because positive and negative are exactly the
         pair that collapses under deuteranopia. */
      candlestick: {
        itemStyle: {
          color: surface, borderColor: positive,          // up: hollow
          color0: negative, borderColor0: negative,       // down: filled
          borderWidth: 1.5,
        },
      },

      /* Sankey: links inherit the node hue at low opacity so a flow is traced
         by eye; the label sits outside the node in ink, not on the fill. */
      sankey: {
        nodeGap: 10,
        itemStyle: { borderWidth: 0 },
        lineStyle: { color: "gradient", opacity: .32, curveness: .5 },
        label: { color: ink, fontSize: 11 },
      },

      /* Continuous encodings take the sequential RAMP, never the categorical
         palette — eight unrelated hues imply eight categories. */
      heatmap:   { itemStyle: { borderColor: surface, borderWidth: 1 },
                   label: { color: ink } },
      visualMap: { inRange: { color: RAMP }, textStyle: { color: muted },
                   borderColor: border },
      dataZoom:  { textStyle: { color: muted }, borderColor: border,
                   fillerColor: "rgba(31, 78, 140, .10)",
                   handleStyle: { color: surface, borderColor: axis },
                   dataBackground: { lineStyle: { color: axis },
                                     areaStyle: { color: grid } } },
      markPoint: { label: { color: surface } },
      markLine:  { lineStyle: { color: muted } },
    };
  };

  docsHtml.register({
    name: "chart-apache-echarts",
    selector: "pre.chart.apache-echarts",

    init(nodes) {
      // Parse every spec FIRST — a bad JSON degrades to source without pulling
      // the ~900 KB engine, and an all-invalid page skips the load entirely.
      const jobs = [];
      for (const pre of nodes) {
        try {
          jobs.push({ pre, option: JSON.parse(pre.textContent), source: pre.textContent });
        } catch (e) {
          docsHtml.chart.markError(pre);   // stays visible; source is the fallback
        }
      }
      if (!jobs.length) return;

      docsHtml.util.loadScript(ECHARTS).then(() => {
        window.echarts.registerTheme(THEME_NAME, buildTheme());

        jobs.forEach(({ pre, option, source }, i) => {
          const frame = new docsHtml.chart.Frame({
            pre, index: i + 1, source,
            copyTitle: "copy ECharts spec",
          });

          // Nudge every chart toward accessible defaults, without overriding
          // an author who set them explicitly.
          if (option.aria === undefined) option.aria = { enabled: true };
          if (option.tooltip === undefined) option.tooltip = {};
          if (option.legend === undefined && Array.isArray(option.series)
              && option.series.length > 1) option.legend = {};

          // "palette:3" / "token:positive" / "ramp:2" -> real values. Presets
          // reference design colours by name so no hex is ever written into a
          // document; see docsHtml.chart.resolveColors.
          docsHtml.chart.resolveColors(option);

          const chart = window.echarts.init(frame.canvas, THEME_NAME, { renderer: "svg" });
          chart.setOption(option);

          // Reflow on width change (responsive labels/layout, still crisp SVG).
          frame.onResize(() => chart.resize());
        });
      }).catch(() => {});   // CDN down → the JSON spec stays visible, readable
    },
  });
})();
