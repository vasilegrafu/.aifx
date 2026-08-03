"""Showcase controller for the `apache-echarts` component.

This one is not like `bar` or `area`, and the difference is the point.

Those wrap the engine: they take `series[] / categories[]` and BUILD an option.
`apache-echarts` IS the engine — it takes an option already written and does
nothing but put it in a `<pre>` for the browser to find. So its contract is not
a shape of series and categories; it is a single string, and the only thing
that can be wrong with that string is that `JSON.parse` will not accept it.

Which is why the context here is JSON TEXT rather than dicts. The macro
interpolates whatever it is given verbatim — there is no `| tojson` in its path
the way there is in charts-apache-echarts/_render.html.j2 — so text is what actually reaches
the reader, and text is therefore what is worth validating.

The states worth seeing are the ones no wrapper component can reach: a chart
form the library does not wrap, a spec naming design colours instead of hexes,
a non-default height, and the degradation path.
"""

import json
import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._showcase_controller import ShowcaseController    # noqa: E402

#: The one key the view passes to the macro that is NOT a valid spec. It is
#: there on purpose, to show the readable-source fallback, so it is the one
#: key _validate_context asserts is broken rather than sound.
DELIBERATELY_BROKEN = "broken"

#: The macro emits data-height only when it differs from this
#: (component.html.j2:12), so the tall section is what makes the attribute
#: observable at all.
DEFAULT_HEIGHT = 340


def _spec(option) -> str:
    """A dict to the JSON text the page will carry.

    Written through json.dumps rather than typed as a string literal for the
    reason charts/line/component.html.j2 gives about hand-written JSON: a
    missed comma fails silently, the chart simply never appears, and what a
    reader sees is indistinguishable from an unreachable CDN."""
    return json.dumps(option, indent=2)


class ChartApacheEchartsShowcaseController(ShowcaseController):

    def _build_context(self):
        # A form the library wraps in NO component, which is the honest reason
        # to reach past the wrappers for the raw engine at all. ECharts reads
        # candlestick data as [open, close, low, high] — note the order, which
        # is not the one the acronym OHLC suggests.
        candlestick = _spec({
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "grid": {"left": 8, "right": 16, "bottom": 8, "containLabel": True},
            "xAxis": {"type": "category",
                      "data": ["Mon", "Tue", "Wed", "Thu", "Fri",
                               "Mon", "Tue", "Wed", "Thu", "Fri"]},
            "yAxis": {"type": "value", "scale": True},
            "series": [{
                "type": "candlestick",
                "name": "Price",
                "data": [[102.4, 104.1, 101.8, 104.6],
                         [104.1, 103.2, 102.7, 105.0],
                         [103.2, 106.8, 103.0, 107.1],
                         [106.8, 106.1, 105.2, 107.4],
                         [106.1, 108.9, 105.9, 109.2],
                         [108.9, 107.4, 106.8, 109.4],
                         [107.4, 110.2, 107.1, 110.8],
                         [110.2, 109.6, 108.4, 110.9],
                         [109.6, 112.3, 109.1, 112.7],
                         [112.3, 111.5, 110.6, 113.0]],
            }],
        })

        # Naming a design colour instead of writing a hex. Resolved in the
        # browser by docsHtml.chart.resolveColors, so the document never
        # carries a colour value and a rebrand does not have to find one.
        # This is for a mark that genuinely needs a specific tone — a target
        # line, a role-coloured node — never for hand-picking a series.
        named_colours = _spec({
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": 8, "right": 16, "bottom": 8, "containLabel": True},
            "xAxis": {"type": "category", "data": ["Q1", "Q2", "Q3", "Q4"]},
            "yAxis": {"type": "value"},
            "series": [{
                "type": "bar",
                "name": "Free cash flow",
                "data": [2.1, 2.6, 3.4, 3.1],
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"color": "token:positive", "type": "dashed"},
                    "data": [{"yAxis": 3.0, "name": "Target"}],
                },
            }],
        })

        # Two axes' worth of categories against one measure — a shape none of
        # the wrappers take, and the second reason to use the engine directly.
        # The ramp is the SEQUENTIAL scale, which is what a magnitude wants;
        # the categorical palette would say these buckets are unrelated.
        heatmap = _spec({
            "tooltip": {"position": "top"},
            "grid": {"left": 8, "right": 16, "bottom": 8, "top": 8,
                     "containLabel": True},
            "xAxis": {"type": "category", "data": ["Q1", "Q2", "Q3", "Q4"],
                      "splitArea": {"show": True}},
            "yAxis": {"type": "category",
                      "data": ["Services", "Hardware", "License", "Cloud"],
                      "splitArea": {"show": True}},
            "visualMap": {"min": 0, "max": 24, "calculable": True,
                          "orient": "horizontal", "left": "center", "bottom": 0,
                          "inRange": {"color": ["ramp:1", "ramp:5"]}},
            "series": [{
                "type": "heatmap",
                "name": "Revenue",
                "label": {"show": True},
                "data": [[0, 0, 4.9], [1, 0, 5.1], [2, 0, 5.4], [3, 0, 5.6],
                         [0, 1, 3.0], [1, 1, 3.2], [2, 1, 3.1], [3, 1, 3.4],
                         [0, 2, 14.1], [1, 2, 14.4], [2, 2, 14.9], [3, 2, 15.2],
                         [0, 3, 19.8], [1, 3, 20.6], [2, 3, 21.9], [3, 3, 23.1]],
            }],
        })

        # NOT a spec, on purpose. The trailing comma after the last element is
        # the single most common way a hand-written option dies, and the
        # fallback it triggers is the one state of this component that cannot
        # be seen any other way. Written as a literal because json.dumps
        # cannot produce invalid JSON.
        broken = (
            '{\n'
            '  "xAxis": { "type": "category", "data": ["Q1", "Q2", "Q3"] },\n'
            '  "yAxis": { "type": "value" },\n'
            '  "series": [{ "type": "bar", "data": [12, 14, 13], }]\n'
            '}'
        )

        return {
            "candlestick": candlestick,
            "named_colours": named_colours,
            "heatmap": heatmap,
            "broken": broken,
            "tall": 480,
        }

    def _validate_context(self, d):
        """The contract of `apache-echarts`: every value the view hands the
        macro is JSON TEXT the browser will accept.

        There is no series/categories shape to check here — this component
        builds nothing, so nothing structural is its responsibility. What IS
        its responsibility is the text, because the macro interpolates it
        verbatim into a `<pre>` and `JSON.parse` in
        js/modules/charts-apache-echarts.js is the next thing to touch it. A
        spec that fails there does not draw a wrong chart; it draws no chart,
        and the reader gets a box of source where a figure was meant to be.

        The wrapped components cannot fail this way — `| tojson` in
        charts-apache-echarts/_render.html.j2 guarantees their output parses — which is
        exactly why the check belongs to this one."""
        SPECS = ("candlestick", "named_colours", "heatmap")

        drawn = {*SPECS, DELIBERATELY_BROKEN, "tall"}
        undrawn = sorted(set(d) - drawn)
        assert not undrawn, \
            (f"apache-echarts: {', '.join(undrawn)} in the context but drawn "
             f"by no section")

        for key in SPECS:
            assert key in d, f"apache-echarts: {key!r} missing from the context"
            spec = d[key]
            assert isinstance(spec, str) and spec.strip(), \
                (f"apache-echarts: {key!r} must be a non-empty str; the macro "
                 f"interpolates it verbatim, it does not serialise it")

            try:
                option = json.loads(spec)
            except json.JSONDecodeError as exc:
                raise AssertionError(
                    f"apache-echarts: {key!r} is not valid JSON ({exc}); the "
                    f"browser would show the source box instead of a chart"
                ) from None

            assert isinstance(option, dict), \
                (f"apache-echarts: {key!r} parses to {type(option).__name__}; "
                 f"an ECharts option is an object")
            series = option.get("series")
            assert isinstance(series, list) and series, \
                (f"apache-echarts: {key!r} has no series; echarts.setOption "
                 f"accepts it and draws an empty card")
            for i, s in enumerate(series):
                assert isinstance(s, dict) and s.get("type"), \
                    (f"apache-echarts: {key!r} series {i} has no type; the "
                     f"engine cannot pick one for you")

            # The rule from usage.md, and the one thing that survives JSON
            # validity while still being wrong. The theme owns the palette, so
            # a hex written into a document opts out of the colourblind-safe
            # guarantee AND out of any future rebrand. Named references
            # (palette:N, token:NAME, ramp:N) are the sanctioned escape.
            assert "#" not in spec, \
                (f"apache-echarts: {key!r} carries a literal colour; the theme "
                 f"owns the palette; name one with palette:N, token:NAME or "
                 f"ramp:N instead")

        # The fallback section only demonstrates the fallback while its spec
        # is genuinely unparseable. Someone tidying this file into valid JSON
        # would leave a section captioned "invalid" that quietly draws a
        # perfectly good bar chart.
        assert DELIBERATELY_BROKEN in d, \
            f"apache-echarts: {DELIBERATELY_BROKEN!r} missing from the context"
        try:
            json.loads(d[DELIBERATELY_BROKEN])
        except json.JSONDecodeError:
            pass
        else:
            raise AssertionError(
                f"apache-echarts: {DELIBERATELY_BROKEN!r} parses cleanly, so "
                f"the section showing the degradation path would draw a normal "
                f"chart and show nothing")

        # The macro writes data-height only when it differs from the default,
        # so an equal value would make that section identical to the others.
        assert isinstance(d["tall"], int) and d["tall"] != DEFAULT_HEIGHT, \
            (f"apache-echarts: tall is {d['tall']!r}; it exists to differ from "
             f"the {DEFAULT_HEIGHT} default, which is what makes the macro emit "
             f"data-height")


if __name__ == "__main__":
    print(ChartApacheEchartsShowcaseController().build())
