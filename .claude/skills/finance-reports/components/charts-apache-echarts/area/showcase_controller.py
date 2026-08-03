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

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import assert_series_categories        # noqa: E402
from components._showcase_controller import ShowcaseController    # noqa: E402

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

        # Two filled regions already overlap; a third hides one of the first
        # two, and the chart still draws. That is the rule from usage.md, and
        # the one thing the shared contract needs told.
        assert_series_categories("area", d, CALLS, max_series=2)

        for axis, series_keys in CALLS:
            for key in series_keys:
                # The fill is drawn from the axis baseline, so a negative point
                # fills DOWNWARD and the two regions read as one shape of
                # ambiguous sign. THE ONE CHECK ONLY `area` CAN MAKE:
                # bar-negative exists for measures that cross zero.
                for i, p in enumerate(d[key]["points"]):
                    assert p >= 0, \
                        (f"area: {key!r} point {i} is {p}; a fill crossing zero "
                         f"reads as one region of ambiguous sign; bar-negative "
                         f"is the component for a measure that goes negative")

        # The dense section earns its place only by crossing the cutoff the
        # macro switches on. If months ever shrank past it, the section would
        # still draw — identically to the others, demonstrating nothing.
        assert len(d["months"]) > SYMBOL_CUTOFF, \
            (f"area: months has {len(d['months'])} categories, not past the "
             f"{SYMBOL_CUTOFF} at which the macro drops point symbols; that "
             f"section is there to show the switch")


if __name__ == "__main__":
    print(ChartAreaShowcaseController().build())
