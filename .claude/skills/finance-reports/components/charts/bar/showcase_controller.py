"""Showcase controller for the `bar` component.

The macro it feeds must match the {# data: … #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]
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
        assert_series_categories("bar", d, (
            ("quarters", ("revenue",)),
            ("quarters", ("fy24", "fy23")),
            ("segments", ("by_segment",)),
            ("segments", ("margin_by_segment",)),
        ))


if __name__ == "__main__":
    print(ChartBarShowcaseController().build())
