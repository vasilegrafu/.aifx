"""Showcase controller for the `funnel` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    stages[] {label:str, value:str, pct:num, note?:str} -- pct is width vs the first stage

pct IS WIDTH AGAINST THE FIRST STAGE, not against the previous one.
The first stage is therefore always 100, and the numbers below are each
recomputed from the top -- the commonest way to draw this wrong is to carry a
stage-to-stage conversion rate into a field that means something else.
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


class FunnelShowcaseController(ShowcaseController):

    def _build_context(self):
        # Widths are each value over the FIRST value: 148/412 = 35.9,
        # 52/412 = 12.6, 38.5/412 = 9.3.
        market = [
            {"label": "Total addressable market", "value": "$412bn", "pct": 100},
            {"label": "Serviceable addressable market", "value": "$148bn",
             "pct": 35.9, "note": "Regions where the product is licensed to sell"},
            {"label": "Serviceable obtainable market", "value": "$52bn",
             "pct": 12.6, "note": "Segments the current product actually fits"},
            {"label": "FY25 revenue", "value": "$38.5bn", "pct": 9.3},
        ]

        # A conversion funnel, where the same rule bites harder: 18,776/128,400
        # = 14.6 and 2,143/128,400 = 1.7, NOT the step-to-step rates.
        conversion = [
            {"label": "Trial signups", "value": "128,400", "pct": 100},
            {"label": "Completed onboarding", "value": "18,776", "pct": 14.6},
            {"label": "Active at 30 days", "value": "9,012", "pct": 7.0},
            {"label": "Converted to paid", "value": "2,143", "pct": 1.7,
             "note": "11.4% of those who finished onboarding"},
        ]
        return {"market": market, "conversion": conversion}

    def _validate_context(self, d):
        """The first stage is 100, widths only narrow, and none exceeds 100.

        A pct above 100 is the valuation-range failure in another component:
        the bar simply runs past its container."""
        assert_all_drawn("funnel", d, [("market", ()), ("conversion", ())])
        for key in ("market", "conversion"):
            stages = d[key]
            assert_rows("funnel", key, stages, ("label", "value", "pct"), 2)
            assert_labels("funnel", f"{key} labels",
                          [s["label"] for s in stages])
            pcts = [s["pct"] for s in stages]
            assert_numbers("funnel", f"{key} pct", pcts)
            assert pcts[0] == 100, \
                (f"funnel: {key} opens at {pcts[0]}, but pct is width against "
                 f"the FIRST stage, so the first stage is 100 by definition")
            for i, p in enumerate(pcts):
                assert 0 < p <= 100, \
                    (f"funnel: {key}[{i}] pct is {p}; outside 0..100 the bar "
                     f"leaves its container")
            assert pcts == sorted(pcts, reverse=True), \
                (f"funnel: {key} widths do not narrow monotonically {pcts}; a "
                 f"stage wider than the one above it is drawn, and reads as a "
                 f"funnel that gains people")

if __name__ == "__main__":
    print(FunnelShowcaseController().build())
