"""Showcase controller for the `stacked-line` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

Each line is drawn at the RUNNING SUM, so the top line is the total.
That is easy to misread as several independent series, so the data here is
unambiguously additive -- headcount by function, where the sum is a real
number someone reports.
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


class ChartStackedLineShowcaseController(ShowcaseController):

    def _build_context(self):
        years = ["FY21", "FY22", "FY23", "FY24", "FY25"]

        engineering = {"name": "Engineering", "points": [4.2, 5.1, 6.4, 7.1, 8.3]}
        sales = {"name": "Sales and marketing", "points": [2.8, 3.2, 3.6, 3.9, 4.4]}
        ga = {"name": "General and administrative",
              "points": [1.1, 1.2, 1.4, 1.5, 1.6]}

        return {
            "years": years,
            "engineering": engineering,
            "sales": sales,
            "ga": ga,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("stacked-line", d, (
            ("years", ("engineering", "sales")),
            ("years", ("engineering", "sales", "ga")),
        ))


if __name__ == "__main__":
    print(ChartStackedLineShowcaseController().build())
