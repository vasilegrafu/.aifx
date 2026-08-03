"""Showcase controller for the `bar-negative` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

THE ZERO LINE IS THE POINT. Every series here genuinely crosses it,
because a bar-negative of all-positive values is a `bar` with extra ceremony --
and the reader learns nothing about the one thing this component does.
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


class ChartBarNegativeShowcaseController(ShowcaseController):

    def _build_context(self):
        quarters = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"]
        segments = ["Cloud", "License", "Hardware", "Services", "Support"]

        # Crosses zero in both directions, which is the whole reason this
        # component exists rather than `bar`.
        surprise = {"name": "EPS surprise",
                    "points": [0.04, -0.02, 0.07, -0.11, 0.03, 0.09, -0.05, 0.12]}

        contribution = {"name": "Contribution to growth",
                        "points": [3.9, 1.2, -2.4, 0.8, -0.6]}

        fy25 = {"name": "FY25", "points": [3.9, 1.2, -2.4, 0.8, -0.6]}
        fy24 = {"name": "FY24", "points": [2.1, -0.4, -1.1, 1.6, 0.3]}

        return {
            "quarters": quarters,
            "segments": segments,
            "surprise": surprise,
            "contribution": contribution,
            "fy25": fy25,
            "fy24": fy24,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("bar-negative", d, (
            ("quarters", ("surprise",)),
            ("segments", ("contribution",)),
            ("segments", ("fy25", "fy24")),
        ))


if __name__ == "__main__":
    print(ChartBarNegativeShowcaseController().build())
