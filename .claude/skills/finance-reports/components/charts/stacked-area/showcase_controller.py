"""Showcase controller for the `stacked-area` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

Composition AND total in one figure, over time. Every series is a
part of one whole and all are non-negative -- a stack containing a negative
band draws a shape whose height is no longer the total, which is the one thing
this component promises.
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


class ChartStackedAreaShowcaseController(ShowcaseController):

    def _build_context(self):
        quarters = ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24",
                    "Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25"]

        cloud = {"name": "Cloud", "points": [5.1, 5.8, 6.4, 7.2, 8.0, 8.9, 9.6, 10.7]}
        license_ = {"name": "License",
                    "points": [4.2, 4.3, 4.4, 4.6, 4.5, 4.6, 4.5, 4.7]}
        hardware = {"name": "Hardware",
                    "points": [1.9, 1.8, 1.9, 2.1, 1.9, 1.8, 1.7, 1.8]}
        services = {"name": "Services",
                    "points": [1.2, 1.2, 1.2, 1.3, 1.5, 1.5, 1.6, 1.7]}

        return {
            "quarters": quarters,
            "cloud": cloud,
            "license": license_,
            "hardware": hardware,
            "services": services,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("stacked-area", d, (
            ("quarters", ("cloud", "license")),
            ("quarters", ("cloud", "license", "hardware", "services")),
        ))


if __name__ == "__main__":
    print(ChartStackedAreaShowcaseController().build())
