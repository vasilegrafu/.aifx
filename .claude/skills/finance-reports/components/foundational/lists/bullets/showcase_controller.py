"""Showcase controller for the `bullets` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items: str[]   -- POSITIONAL AND REQUIRED, bullets(items)

BULLETS ARE FOR PARALLEL, UNRANKED POINTS. If the order carries
meaning use `numbered`; if the reader is meant to do them use `steps`. The
three render similarly and mean different things, which is why they are three
components rather than one with a flag.
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


class BulletsShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"items": [
            "Net retention fell to 104% from 111%, the fourth consecutive "
            "quarterly decline.",
            "Free cash flow of $2,530m covered the dividend 2.4 times.",
            "The leverage covenant is next tested at FY26 Q2, at 1.13x "
            "against a 2.5x limit.",
            "FY26 guidance was withdrawn on 28 January and has not been "
            "reissued.",
        ]}

    def _validate_context(self, d):
        """Distinct, non-empty items."""
        assert_all_drawn("bullets", d, [("items", ())])
        assert_labels("bullets", "items", d["items"])

if __name__ == "__main__":
    print(BulletsShowcaseController().build())
