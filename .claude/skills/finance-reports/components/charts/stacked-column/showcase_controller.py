"""Showcase controller for the `stacked-column` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

Parts summing to a whole ACROSS CATEGORIES rather than over time --
the categories here are entities, not periods, which is what separates this
from stacked-area.
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


class ChartStackedColumnShowcaseController(ShowcaseController):

    def _build_context(self):
        peers = ["AMD", "NVDA", "INTC", "QCOM", "AVGO"]

        data_center = {"name": "Data centre",
                       "points": [16.6, 47.5, 15.5, 6.4, 28.2]}
        client = {"name": "Client",
                  "points": [14.6, 3.1, 30.1, 24.7, 4.9]}
        embedded = {"name": "Embedded",
                    "points": [3.5, 1.4, 8.2, 5.1, 12.6]}

        return {
            "peers": peers,
            "data_center": data_center,
            "client": client,
            "embedded": embedded,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("stacked-column", d, (
            ("peers", ("data_center", "client")),
            ("peers", ("data_center", "client", "embedded")),
        ))


if __name__ == "__main__":
    print(ChartStackedColumnShowcaseController().build())
