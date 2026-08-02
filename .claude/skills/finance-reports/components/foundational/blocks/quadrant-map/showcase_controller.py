"""Showcase controller for the `quadrant-map` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {label:str, x:0-100, y:0-100, tone?:str}   quadrants: str[4]

THE QUADRANT ORDER IS z1..z4 = TOP-LEFT, TOP-RIGHT, BOTTOM-LEFT,
BOTTOM-RIGHT, and items are placed with left:x and bottom:y -- so y=100 is the
TOP. Reading the list as reading order is the easy mistake, and it puts every
label in the wrong corner without anything failing.

Items near 0 or 100 push their label off the plot, so these sit in 15..85.
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


class QuadrantMapShowcaseController(ShowcaseController):

    def _build_context(self):
        # x is share, y is growth. y is applied as `bottom`, so 81 is near the
        # top: Vertex is the high-growth, low-share challenger.
        items = [
            {"label": "Northwind", "x": 78, "y": 72, "tone": "good"},
            {"label": "Vertex", "x": 24, "y": 81},
            {"label": "Halcyon", "x": 84, "y": 28},
            {"label": "Pemberly", "x": 18, "y": 22, "tone": "bad"},
            {"label": "Arden", "x": 52, "y": 54},
        ]
        # z1 top-left, z2 top-right, z3 bottom-left, z4 bottom-right.
        quadrants = ["Challengers", "Leaders", "Niche", "Incumbents"]
        return {"items": items, "quadrants": quadrants}

    def _validate_context(self, d):
        """Four quadrant names, and every item inside the plot with room for
        its label."""
        assert_rows("quadrant-map", "items", d["items"], ("label", "x", "y"), 2)
        assert_all_drawn("quadrant-map", d, [("items", ("quadrants",))])
        assert_labels("quadrant-map", "item labels",
                      [i["label"] for i in d["items"]])
        assert_labels("quadrant-map", "quadrants", d["quadrants"])
        assert len(d["quadrants"]) == 4, \
            (f"quadrant-map: {len(d['quadrants'])} quadrant names; the macro "
             f"places them at z1..z4 and a fifth would be positioned nowhere")
        for i in d["items"]:
            assert_numbers("quadrant-map", i["label"], [i["x"], i["y"]])
            for axis in ("x", "y"):
                assert 15 <= i[axis] <= 85, \
                    (f"quadrant-map: {i['label']!r} has {axis}={i[axis]}; "
                     f"inside 0..100 but close enough to the edge that the "
                     f"label runs outside the plot frame")
            if "tone" in i:
                assert_enum("quadrant-map", f"items[{i['label']!r}].tone",
                            i["tone"], {"good", "bad"})

if __name__ == "__main__":
    print(QuadrantMapShowcaseController().build())
