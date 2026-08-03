"""Showcase controller for the `funnel-chart` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    stages[] {name:str, value:num}

A FUNNEL NARROWS. _validate_context enforces monotonic decrease,
because a stage larger than the one above it draws a band wider than its
parent -- a shape that is not a funnel and describes a process that cannot
happen.
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


class ChartFunnelChartShowcaseController(ShowcaseController):

    def _build_context(self):
        # Each stage is a subset of the one before it, which is what makes
        # the shape a funnel rather than a stack of unrelated bars.
        pipeline = [
            {"name": "Qualified leads", "value": 12400},
            {"name": "Proof of concept", "value": 6850},
            {"name": "Contract issued", "value": 2910},
            {"name": "Closed won", "value": 1640},
        ]

        # A shallower funnel, where the drop-off is the finding rather than
        # the shape.
        design_wins = [
            {"name": "Design engagements", "value": 480},
            {"name": "Design wins", "value": 412},
            {"name": "In production", "value": 366},
        ]

        return {"pipeline": pipeline, "design_wins": design_wins}

    def _validate_context(self, d):
        """MONOTONIC DECREASE -- the check only a funnel can make.

        A stage larger than its parent draws a band wider than the one above
        it: a picture of a process where more comes out than went in."""
        for key in ("pipeline", "design_wins"):
            stages = d[key]
            assert_labels("funnel-chart", f"{key} names", [s["name"] for s in stages])
            values = [s["value"] for s in stages]
            assert_numbers("funnel-chart", f"{key} values", values)
            assert len(stages) >= 2, \
                f"funnel-chart: {key} has one stage; a funnel needs a narrowing"
            for i in range(1, len(values)):
                assert values[i] <= values[i - 1], \
                    (f"funnel-chart: {key} rises from {values[i-1]} to "
                     f"{values[i]} at {stages[i]['name']!r}; a funnel narrows, "
                     f"and a widening band shows more leaving than entered")

if __name__ == "__main__":
    print(ChartFunnelChartShowcaseController().build())
