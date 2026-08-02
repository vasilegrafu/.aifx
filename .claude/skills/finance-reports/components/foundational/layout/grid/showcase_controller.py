"""Showcase controller for the `grid` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    grid(min="14rem")   -- the SMALLEST a tile may be before the grid rewraps

`min` IS A FLOOR, NOT A WIDTH. The grid auto-fits as many tiles as
fit at that minimum and shares the remainder between them, so raising `min`
gives FEWER, WIDER tiles rather than wider tiles in the same arrangement. The
two sections below differ only in that number.
"""

import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import (                                # noqa: E402
    assert_all_drawn, assert_enum, assert_labels, assert_numbers, assert_rows)
from components._showcase_controller import ShowcaseController     # noqa: E402


class GridShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"tiles": [
            {"title": "Revenue", "body": "$38,549m, up 12.7%"},
            {"title": "Gross profit", "body": "$19,081m, up 8.4%"},
            {"title": "Operating income", "body": "$5,748m, 0.8% above budget"},
            {"title": "Net income", "body": "$5,136m, up 6.2%"},
            {"title": "Free cash flow", "body": "$2,530m, up 18.2%"},
            {"title": "Net debt", "body": "$8,185m, up 3.5%"},
        ], "tight": "12rem", "loose": "22rem"}

    def _validate_context(self, d):
        """Six distinct tiles, and two different minimums to compare."""
        assert_all_drawn("grid", d, [("tiles", ("tight", "loose"))])
        assert_rows("grid", "tiles", d["tiles"], ("title", "body"), 4)
        assert_labels("grid", "tile titles", [t["title"] for t in d["tiles"]])
        for key in ("tight", "loose"):
            assert d[key].endswith("rem"), \
                (f"grid: {key} is {d[key]!r}; --grid-min is a CSS length and "
                 f"a bare number is ignored, leaving the 14rem default")
        assert d["tight"] != d["loose"], \
            "grid: both minimums are equal, which compares nothing"

if __name__ == "__main__":
    print(GridShowcaseController().build())
