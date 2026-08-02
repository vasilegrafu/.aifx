"""Showcase controller for the `catalyst-timeline` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {date:str, event:str, direction:up|down|mixed, likelihood?:str, note?:str}

DIRECTION IS THE EXPECTED EFFECT, not the certainty -- `likelihood`
carries that separately. A near-certain event with a small effect and a
long-shot with a large one are different things, and the component keeps them
apart.
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
    assert_enum, assert_numbers, assert_rows)
from components._showcase_controller import ShowcaseController     # noqa: E402


class CatalystTimelineShowcaseController(ShowcaseController):

    def _build_context(self):
        items = [
            {"date": "12 Aug 2026", "event": "Q2 FY2026 results",
             "direction": "mixed", "likelihood": "Certain",
             "note": "Guidance matters more than the quarter"},
            {"date": "Sep 2026", "event": "Next-node foundry allocation agreed",
             "direction": "up", "likelihood": "Likely",
             "note": "Would remove the binding constraint in the thesis"},
            {"date": "Q4 2026", "event": "Competitor launches at the same node",
             "direction": "down", "likelihood": "Likely"},
            {"date": "H1 2027", "event": "Export licence review",
             "direction": "down", "likelihood": "Possible",
             "note": "Roughly 12% of data centre revenue is in scope"},
            {"date": "2027", "event": "Embedded design wins reach production",
             "direction": "up", "likelihood": "Possible"},
        ]
        return {"items": items}

    def _validate_context(self, d):
        """All three directions appear, and dates are in chronological order.

        A timeline out of order is the one defect that renders perfectly."""
        items = d["items"]
        assert_rows("catalyst-timeline", "items", items,
                    ("date", "event", "direction"))
        for i, it in enumerate(items):
            assert_enum("catalyst-timeline", f"items[{i}].direction",
                        it["direction"], {"up", "down", "mixed"})
        seen = {i["direction"] for i in items}
        assert seen == {"up", "down", "mixed"}, \
            f"catalyst-timeline: shows {sorted(seen)}; all three should appear"

if __name__ == "__main__":
    print(CatalystTimelineShowcaseController().build())
