"""Showcase controller for the `line` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

Time on x, always left to right -- the slope between two unordered
categories means nothing, which is the mistake usage.md warns against. Every
series here is a measure over consecutive periods.
"""

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


class ChartLineShowcaseController(ShowcaseController):

    def _build_context(self):
        quarters = ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24",
                    "Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25"]

        revenue = {"name": "Revenue",
                   "points": [12.4, 13.1, 13.9, 15.2, 15.9, 16.8, 17.4, 18.9]}
        fy25 = {"name": "FY25", "points": [15.9, 16.8, 17.4, 18.9]}
        fy24 = {"name": "FY24", "points": [12.4, 13.1, 13.9, 15.2]}

        # A rate, not a level: `line` is the right component precisely because
        # nothing is filled underneath, so no area implies a quantity.
        gross_margin = {"name": "Gross margin",
                        "points": [48.2, 48.9, 49.4, 49.1, 50.3, 51.0, 51.4, 52.2]}

        return {
            "quarters": quarters,
            "half": ["Q1", "Q2", "Q3", "Q4"],
            "revenue": revenue,
            "fy25": fy25,
            "fy24": fy24,
            "gross_margin": gross_margin,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("line", d, (
            ("quarters", ("revenue",)),
            ("half", ("fy25", "fy24")),
            ("quarters", ("gross_margin",)),
        ))


if __name__ == "__main__":
    print(ChartLineShowcaseController().build())
