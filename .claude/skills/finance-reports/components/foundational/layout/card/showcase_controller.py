"""Showcase controller for the `card` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    card(title="")   -- the title line is dropped when empty

THE CARD IS THE CELL UNIT for `columns` and `grid`. On its own it is
a bordered surface with an optional title; the reason it exists is that a grid
of bare components has nothing to align, and a grid of cards does.
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


class CardShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"titles": ["Balance sheet", "Cash generation", "Leverage"],
                "bodies": [
                    "Net debt of $8,185m against EBITDA of $7,240m.",
                    "Free cash flow of $2,530m, covering the dividend 2.4x.",
                    "1.13x net debt to EBITDA, inside the 2.5x covenant.",
                ]}

    def _validate_context(self, d):
        """One body per title, all distinct."""
        assert_all_drawn("card", d, [("titles", ("bodies",))])
        assert_labels("card", "titles", d["titles"])
        assert_labels("card", "bodies", d["bodies"])
        assert len(d["titles"]) == len(d["bodies"]), \
            "card: every title needs its own body"

if __name__ == "__main__":
    print(CardShowcaseController().build())
