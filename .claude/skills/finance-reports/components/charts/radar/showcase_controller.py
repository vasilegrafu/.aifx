"""Showcase controller for the `radar` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    indicators[] {name:str, max:num|null}   series[] {name:str, points:num[]}

THREE SERIES MAXIMUM -- past that it is a web, per usage.md, and
_validate_context enforces it. Axis order is fixed deliberately and kept the
same across both figures, because the same data in another order draws a
different polygon and neither is more true.
"""

import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import assert_labels, assert_numbers    # noqa: E402
from components._showcase_controller import ShowcaseController     # noqa: E402


class ChartRadarShowcaseController(ShowcaseController):

    def _build_context(self):
        # ONE order, used by both figures. usage.md: "axis order changes the
        # shape ... fix the order deliberately and keep it across figures".
        indicators = [
            {"name": "Growth", "max": 100},
            {"name": "Margin", "max": 100},
            {"name": "Returns", "max": 100},
            {"name": "Balance sheet", "max": 100},
            {"name": "Valuation", "max": 100},
            {"name": "Momentum", "max": 100},
        ]

        amd = {"name": "AMD", "points": [82, 51, 24, 74, 31, 68]}
        nvda = {"name": "NVDA", "points": [96, 88, 94, 88, 12, 91]}
        intc = {"name": "INTC", "points": [18, 22, 8, 41, 79, 21]}

        return {"indicators": indicators, "amd": amd, "nvda": nvda, "intc": intc}

    def _validate_context(self, d):
        """Three series maximum, and every point inside its indicator's max.

        A point past the maximum is drawn AT the maximum, so the polygon is
        silently wrong rather than out of bounds."""
        indicators = d["indicators"]
        assert_labels("radar", "indicator names", [i["name"] for i in indicators])

        keys = ("amd", "nvda", "intc")
        assert len(keys) <= 3, \
            (f"radar: {len(keys)} series; usage.md caps it at three, past which "
             f"the overlapping polygons are a web")

        for key in keys:
            s = d[key]
            assert isinstance(s.get("name"), str) and s["name"], \
                f"radar: {key!r} needs a non-empty name"
            points = s["points"]
            assert_numbers("radar", f"{key!r} points", points)
            assert len(points) == len(indicators), \
                (f"radar: {key!r} has {len(points)} points against "
                 f"{len(indicators)} indicators; ECharts pairs them by index "
                 f"and drops the difference in silence")
            for i, (p, ind) in enumerate(zip(points, indicators)):
                assert 0 <= p <= ind["max"], \
                    (f"radar: {key!r} scores {p} on {ind['name']!r}, outside "
                     f"0..{ind['max']}; it would be clamped to the axis and the "
                     f"polygon would draw a value nobody supplied")

if __name__ == "__main__":
    print(ChartRadarShowcaseController().build())
