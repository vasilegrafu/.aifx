"""Showcase controller for the `area` component.

The macro it feeds must match the {# data: … #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

Same shape as `bar`, and deliberately so — but the DATA is chosen differently.
`area` fills the region beneath the line, which claims the quantity under it is
real, so every series here is a level or a cumulative flow with a meaningful
zero. Nothing in this file is a ratio, a rate or a price: those belong to
`line`, and a showcase that used one would be demonstrating the mistake its
usage.md warns against.
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

#: Past this many categories the macro drops the point symbols
#: (component.html.j2:14) and the line alone carries the shape. One section
#: exists to cross it, so the number is named rather than written twice.
SYMBOL_CUTOFF = 24


class ChartAreaShowcaseController(ShowcaseController):

    def _build_context(self):
        quarters = ["Q1", "Q2", "Q3", "Q4"]

        # One series, one meaningful zero: cash on hand is a LEVEL, so the
        # area beneath it is the quantity actually held.
        cash = {"name": "Cash and equivalents", "points": [8.2, 9.6, 11.3, 12.1]}

        # Two series, the documented maximum. Overlapping translucent fills
        # stop being readable past this — beyond two the component to reach
        # for is stacked-area, which is why no section here draws three.
        fy24 = {"name": "FY24", "points": [8.2, 9.6, 11.3, 12.1]}
        fy23 = {"name": "FY23", "points": [6.9, 7.4, 8.8, 9.2]}

        # Cumulative flow — the other honest use of a fill. It only rises,
        # and the area under it is the total spent to date.
        capex_ytd = {"name": "Capex, cumulative",
                     "points": [1.4, 3.1, 4.9, 7.2]}

        # 36 months, past SYMBOL_CUTOFF, so the macro drops the symbols and
        # the fill carries the shape on its own. Built rather than written out
        # because a hand-typed 36-point list is a list nobody checks.
        months = [f"{y}-{m:02d}" for y in (2022, 2023, 2024) for m in range(1, 13)]
        backlog = {"name": "Backlog",
                   "points": [round(14.0 + i * 0.42 + 1.6 * math.sin(i / 2.4), 2)
                              for i in range(len(months))]}

        return {
            "quarters": quarters,
            "months": months,
            "cash": cash,
            "fy24": fy24,
            "fy23": fy23,
            "capex_ytd": capex_ytd,
            "backlog": backlog,
        }

    def _validate_context(self, d):
        """The {# data: … #} contract of `area`, against every call the view
        makes:

            series[] {name:str, points:num[]}   categories: str[]

        CALLS is the five <section>s of showcase.html.j2, one entry each, read
        as categories -> the series drawn against them. PER SECTION rather
        than grouped by axis, because the two checks that matter are both
        relative: points against ITS categories, and names against the OTHER
        names in the same legend. A section added to the view is an entry
        added here."""
        CALLS = (
            ("quarters", ("cash",)),
            ("quarters", ("fy24", "fy23")),
            ("quarters", ("capex_ytd",)),
            ("months", ("backlog",)),
        )

        # Nothing in the context goes undrawn. Every other check runs from
        # CALLS to the context; this one runs back, and it is what notices a
        # section the view renamed or data orphaned by one it deleted.
        drawn = {name for axis, keys in CALLS for name in (axis, *keys)}
        undrawn = sorted(set(d) - drawn)
        assert not undrawn, \
            f"area: {', '.join(undrawn)} in the context but drawn by no section"

        for axis, series_keys in CALLS:
            assert axis in d, f"area: {axis!r} missing from the context"
            categories = d[axis]
            assert isinstance(categories, list) and categories, \
                f"area: {axis!r} must be a non-empty list"
            assert all(isinstance(c, str) and c for c in categories), \
                f"area: {axis!r} must hold non-empty str; they are the xAxis ticks"
            repeated = sorted({c for c in categories if categories.count(c) > 1})
            assert not repeated, \
                (f"area: {axis!r} repeats {', '.join(map(repr, repeated))}; two "
                 f"ticks a reader cannot tell apart, and a tooltip that picks "
                 f"whichever came first")

            # The rule from usage.md, and the only check here `bar` has no
            # reason to make. Two filled regions already overlap; a third
            # hides one of the first two, and the chart still draws.
            assert len(series_keys) <= 2, \
                (f"area: {len(series_keys)} series against {axis!r}; overlapping "
                 f"fills hide one another past two; stacked-area is the "
                 f"component for that")

            for key in series_keys:
                assert key in d, f"area: {key!r} missing from the context"
                series = d[key]
                assert isinstance(series, dict), \
                    (f"area: {key!r} must be a dict of name and points, got "
                     f"{type(series).__name__}")
                assert isinstance(series.get("name"), str) and series["name"], \
                    f"area: {key!r} needs a non-empty str name, which labels the legend"
                points = series.get("points")
                assert isinstance(points, list) and points, \
                    f"area: {key!r} needs a non-empty list of points"

                for i, p in enumerate(points):
                    assert isinstance(p, (int, float)) and not isinstance(p, bool), \
                        (f"area: {key!r} point {i} is {p!r}; points must be "
                         f"numbers, they go straight to ECharts")
                    # NaN and the infinities pass every isinstance test above
                    # and reach _render.html.j2's `| tojson`, which writes them
                    # into the <pre> as bare NaN / Infinity. That is not JSON,
                    # so charts-apache-echarts.js throws on JSON.parse and the
                    # page shows no chart at all. Caught here, it costs a line.
                    assert math.isfinite(p), \
                        (f"area: {key!r} point {i} is {p!r}; tojson writes it "
                         f"unquoted and the browser's JSON.parse rejects it, "
                         f"so the chart never renders")
                    # JS has one number type, float64, so an integer past
                    # 2**53 arrives rounded. Floats are already float64 in
                    # Python and round-trip exactly, so only ints can lose.
                    assert not isinstance(p, int) or abs(p) <= JS_SAFE_INT, \
                        (f"area: {key!r} point {i} is {p}, past JavaScript's "
                         f"safe integer range; it would arrive rounded")
                    # The fill is drawn from the axis baseline, so a negative
                    # point fills DOWNWARD and the two regions read as one
                    # shape of ambiguous sign. bar-negative exists for
                    # measures that cross zero; a filled area does not.
                    assert p >= 0, \
                        (f"area: {key!r} point {i} is {p}; a fill crossing zero "
                         f"reads as one region of ambiguous sign; bar-negative "
                         f"is the component for a measure that goes negative")

                # The check StrictUndefined cannot make. ECharts pairs series
                # to categories BY INDEX and complains about neither a short
                # nor a long list: the chart draws, and the surplus is simply
                # not there to see.
                assert len(points) == len(categories), \
                    (f"area: {key!r} has {len(points)} points against "
                     f"{len(categories)} {axis}; the chart would draw and drop "
                     f"the difference silently")

            # From two series up the macro adds a legend (component.html.j2:30)
            # and the legend is keyed BY NAME, so duplicates collapse into one
            # entry and one of the fills becomes unlabelled. Per section, not
            # global, exactly as in bar.
            names = [d[key]["name"] for key in series_keys]
            repeated = sorted({n for n in names if names.count(n) > 1})
            assert not repeated, \
                (f"area: {' and '.join(series_keys)} share the name "
                 f"{', '.join(map(repr, repeated))}; one legend key would "
                 f"stand for both")

        # The dense section earns its place only by crossing the cutoff the
        # macro switches on. If months ever shrank past it, the section would
        # still draw — identically to the others, demonstrating nothing.
        assert len(d["months"]) > SYMBOL_CUTOFF, \
            (f"area: months has {len(d['months'])} categories, not past the "
             f"{SYMBOL_CUTOFF} at which the macro drops point symbols; that "
             f"section is there to show the switch")


if __name__ == "__main__":
    print(ChartAreaShowcaseController().build())
