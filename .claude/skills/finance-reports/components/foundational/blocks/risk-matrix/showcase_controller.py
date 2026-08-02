"""Showcase controller for the `risk-matrix` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {id:str, probability:1-5, impact:1-5, label:str}

PROBABILITY AND IMPACT ARE 1..5 INCLUSIVE. The macro draws the grid
by iterating 1..5 and placing a chip where an item matches, so an item at 0 or
6 matches no cell -- it does not raise, it simply never appears, and the
matrix looks complete without it.

The cell colour is p x i, banded at >12 high and >4 medium. That is the
macro's own arithmetic, not something the data controls.
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


class RiskMatrixShowcaseController(ShowcaseController):

    def _build_context(self):
        items = [
            {"id": "R1", "probability": 5, "impact": 4,
             "label": "Single-source supplier for the controller board"},
            {"id": "R2", "probability": 3, "impact": 5,
             "label": "Covenant breach if EBITDA falls a further 12%"},
            {"id": "R3", "probability": 2, "impact": 2,
             "label": "Key-person dependency in group tax"},
            {"id": "R4", "probability": 4, "impact": 2,
             "label": "FX translation drag on reported revenue"},
            {"id": "R5", "probability": 1, "impact": 5,
             "label": "Regulatory ban in the largest market"},
            {"id": "R6", "probability": 3, "impact": 3,
             "label": "Platform migration slips past Q3"},
        ]
        return {"items": items}

    def _validate_context(self, d):
        """Every item lands in a real cell, and no two share one.

        Out of range is the silent failure: the chip is drawn by no cell and
        the risk vanishes from a matrix that still looks full. Two in one cell
        is merely cramped, but it is worth knowing about."""
        assert_rows("risk-matrix", "items", d["items"],
                    ("id", "probability", "impact", "label"), 2)
        assert_all_drawn("risk-matrix", d, [("items", ())])
        assert_labels("risk-matrix", "ids", [i["id"] for i in d["items"]])
        assert_labels("risk-matrix", "labels", [i["label"] for i in d["items"]])
        seen = {}
        for it in d["items"]:
            for axis in ("probability", "impact"):
                value = it[axis]
                assert isinstance(value, int) and 1 <= value <= 5, \
                    (f"risk-matrix: {it['id']} has {axis}={value!r}; the grid "
                     f"is drawn over 1..5 and anything else matches no cell, "
                     f"so the risk silently disappears")
            cell = (it["probability"], it["impact"])
            assert cell not in seen, \
                (f"risk-matrix: {it['id']} and {seen[cell]} both sit at "
                 f"probability {cell[0]}, impact {cell[1]}; the chips stack "
                 f"in one cell")
            seen[cell] = it["id"]

if __name__ == "__main__":
    print(RiskMatrixShowcaseController().build())
