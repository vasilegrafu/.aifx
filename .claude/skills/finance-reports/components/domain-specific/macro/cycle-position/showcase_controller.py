"""Showcase controller for the `cycle-position` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    phases[] {label:str, note?:str}   at: 0-based index of the current phase

`at` IS A 0-BASED INDEX AND NOTHING BOUNDS IT. The macro marks the
phase where loop.index0 == at, so an `at` past the end marks NOTHING -- the
band renders complete, with no current phase and no error. Off by one, it
marks the wrong phase just as quietly.
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


class CyclePositionShowcaseController(ShowcaseController):

    def _build_context(self):
        phases = [
            {"label": "Early expansion",
             "note": "Credit loosening, spare capacity"},
            {"label": "Mid expansion",
             "note": "Capacity tightening, margins peak"},
            {"label": "Late expansion",
             "note": "Wage pressure, policy turns restrictive"},
            {"label": "Contraction",
             "note": "Inventories clear, defaults rise"},
        ]
        return {"phases": phases, "at": 2}

    def _validate_context(self, d):
        """The index lands on a real phase.

        Out of range does not raise: the band renders with nothing marked,
        which reads as a diagram rather than as a claim."""
        assert_rows("cycle-position", "phases", d["phases"], ("label",), 2)
        assert_all_drawn("cycle-position", d, [("phases", ("at",))])
        assert_labels("cycle-position", "phase labels",
                      [p["label"] for p in d["phases"]])
        assert isinstance(d["at"], int) and not isinstance(d["at"], bool), \
            f"cycle-position: at is {d['at']!r}; it is a 0-based index"
        assert 0 <= d["at"] < len(d["phases"]), \
            (f"cycle-position: at={d['at']} against {len(d['phases'])} "
             f"phases; the band would render with no phase marked at all")

if __name__ == "__main__":
    print(CyclePositionShowcaseController().build())
