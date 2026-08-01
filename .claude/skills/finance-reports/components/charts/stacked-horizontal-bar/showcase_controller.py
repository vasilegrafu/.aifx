"""Showcase controller for the `stacked-horizontal-bar` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

FOR LONG CATEGORY NAMES -- that is the only reason to prefer it over
stacked-column, so every category here is genuinely long. Short labels would
render fine and demonstrate nothing.
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


class ChartStackedHorizontalBarShowcaseController(ShowcaseController):

    def _build_context(self):
        # Genuinely long -- a vertical axis would have to rotate these, which
        # is the whole reason this component exists. They need more room than
        # `containLabel` will give on its own, so both sections pass
        # `label_room`.
        categories = [
            "Data centre and accelerated computing",
            "Client computing and consumer graphics",
            "Embedded and industrial systems",
            "Professional visualisation and design",
            "Automotive and autonomous platforms",
        ]

        product = {"name": "Product", "points": [14.2, 11.8, 2.9, 1.4, 0.9]}
        support = {"name": "Support and services",
                   "points": [2.4, 2.7, 0.6, 0.5, 0.3]}
        licensing = {"name": "Licensing", "points": [0.9, 0.4, 0.2, 0.1, 0.1]}

        return {
            "categories": categories,
            "product": product,
            "support": support,
            "licensing": licensing,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("stacked-horizontal-bar", d, (
            ("categories", ("product", "support")),
            ("categories", ("product", "support", "licensing")),
        ))


if __name__ == "__main__":
    print(ChartStackedHorizontalBarShowcaseController().build())
