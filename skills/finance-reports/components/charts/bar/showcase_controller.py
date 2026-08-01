"""Showcase controller for the `bar` component.

The macro it feeds must match the {# data: … #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]
"""

import math
import sys
from pathlib import Path

# The skill root on sys.path, so the base imports PACKAGE-QUALIFIED — ONE
# module object, and therefore the one cached env() every controller shares. A
# bare `from _showcase_controller import` would resolve too, but as a second
# module for anything that reached it the other way, and each copy would parse
# the component tree again. Found by walking up rather than by a fixed index:
# components sit two to four folders deep depending on their category.
_SKILL_DIR = next(p.parent for p in Path(__file__).resolve().parents if p.name == "components")
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._showcase_controller import ShowcaseController    # noqa: E402

#: Number.MAX_SAFE_INTEGER. The page parses its data with JSON.parse, where
#: every number becomes a float64, so an integer past this arrives rounded.
JS_SAFE_INT = 2 ** 53 - 1


class ChartBarShowcaseController(ShowcaseController):

    def _build_context(self):
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        segments = ["Cloud", "License", "Hardware", "Services"]
        fy24 = {"name": "FY24", "points": [12.4, 13.1, 13.9, 15.2]}
        fy23 = {"name": "FY23", "points": [10.8, 11.5, 12.2, 13.0]}

        revenue = {"name": "Revenue", "points": [12.4, 13.1, 13.9, 15.2]}
        by_segment = {"name": "FY24", "points": [22.1, 14.7, 3.2, 5.4]}
        margin_by_segment = {"name": "FY24", "points": [31.2, 88.4, 9.1, 24.7]}

        return {
            "quarters": quarters,
            "segments": segments,
            "revenue": revenue,
            "fy24": fy24,
            "fy23": fy23,
            "by_segment": by_segment,
            "margin_by_segment": margin_by_segment,
        }

    def _validate_context(self, d):
        """The {# data: … #} contract of `bar`, against every call the view
        makes:

            series[] {name:str, points:num[]}   categories: str[]

        CALLS is the four <section>s of showcase.html.j2, one entry each, read
        as categories -> the series drawn against them. PER SECTION rather
        than grouped by axis, because the two checks that matter are both
        relative: points against ITS categories, and names against the OTHER
        names in the same legend. A section added to the view is an entry
        added here."""
        CALLS = (
            ("quarters", ("revenue",)),
            ("quarters", ("fy24", "fy23")),
            ("segments", ("by_segment",)),
            ("segments", ("margin_by_segment",)),
        )

        # Nothing in the context goes undrawn. Every other check runs from
        # CALLS to the context; this one runs back, and it is what notices a
        # section the view renamed or data orphaned by one it deleted.
        drawn = {name for axis, keys in CALLS for name in (axis, *keys)}
        undrawn = sorted(set(d) - drawn)
        assert not undrawn, \
            f"bar: {', '.join(undrawn)} in the context but drawn by no section"

        for axis, series_keys in CALLS:
            assert axis in d, f"bar: {axis!r} missing from the context"
            categories = d[axis]
            assert isinstance(categories, list) and categories, \
                f"bar: {axis!r} must be a non-empty list"
            assert all(isinstance(c, str) and c for c in categories), \
                f"bar: {axis!r} must hold non-empty str; they are the xAxis ticks"
            repeated = sorted({c for c in categories if categories.count(c) > 1})
            assert not repeated, \
                (f"bar: {axis!r} repeats {', '.join(map(repr, repeated))}; two "
                 f"ticks a reader cannot tell apart, and a tooltip that picks "
                 f"whichever came first")

            for key in series_keys:
                assert key in d, f"bar: {key!r} missing from the context"
                series = d[key]
                assert isinstance(series, dict), \
                    (f"bar: {key!r} must be a dict of name and points, got "
                     f"{type(series).__name__}")
                assert isinstance(series.get("name"), str) and series["name"], \
                    f"bar: {key!r} needs a non-empty str name, which labels the legend"
                points = series.get("points")
                assert isinstance(points, list) and points, \
                    f"bar: {key!r} needs a non-empty list of points"

                for i, p in enumerate(points):
                    assert isinstance(p, (int, float)) and not isinstance(p, bool), \
                        (f"bar: {key!r} point {i} is {p!r}; points must be "
                         f"numbers, they go straight to ECharts")
                    # NaN and the infinities pass every isinstance test above
                    # and reach _render.html.j2's `| tojson`, which writes them
                    # into the <pre> as bare NaN / Infinity. That is not JSON,
                    # so charts-apache-echarts.js throws on JSON.parse and the
                    # page shows no chart at all. Caught here, it costs a line.
                    assert math.isfinite(p), \
                        (f"bar: {key!r} point {i} is {p!r}; tojson writes it "
                         f"unquoted and the browser's JSON.parse rejects it, "
                         f"so the chart never renders")
                    # JS has one number type, float64, so an integer past
                    # 2**53 arrives rounded. Floats are already float64 in
                    # Python and round-trip exactly, so only ints can lose.
                    assert not isinstance(p, int) or abs(p) <= JS_SAFE_INT, \
                        (f"bar: {key!r} point {i} is {p}, past JavaScript's "
                         f"safe integer range; it would arrive rounded")

                # The check StrictUndefined cannot make. ECharts pairs series
                # to categories BY INDEX and complains about neither a short
                # nor a long list: the chart draws, and the surplus is simply
                # not there to see.
                assert len(points) == len(categories), \
                    (f"bar: {key!r} has {len(points)} points against "
                     f"{len(categories)} {axis}; the chart would draw and drop "
                     f"the difference silently")

            # From two series up the macro adds a legend (component.html.j2:31)
            # and the legend is keyed BY NAME, so duplicates collapse into one
            # entry and one of the bars becomes unlabelled. Per section, not
            # global: by_segment and margin_by_segment are both "FY24" and that
            # is correct, because no section draws them together.
            names = [d[key]["name"] for key in series_keys]
            repeated = sorted({n for n in names if names.count(n) > 1})
            assert not repeated, \
                (f"bar: {' and '.join(series_keys)} share the name "
                 f"{', '.join(map(repr, repeated))}; one legend key would "
                 f"stand for both")


if __name__ == "__main__":
    print(ChartBarShowcaseController().build())
