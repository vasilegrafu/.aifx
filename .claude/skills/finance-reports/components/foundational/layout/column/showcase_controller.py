"""Showcase controller for the `column` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    column(span=1)   -- span>1 sets flex-grow, making the cell wider

`span` IS flex-grow, NOT A COLUMN COUNT. span=2 beside span=1 gives
two thirds and one third; span=2 beside span=2 gives halves. It is a RATIO
against its siblings, so changing one cell changes the meaning of every other
cell in the row -- which is the opposite of how a twelve-column grid behaves
and is the mistake worth naming.
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


class ColumnShowcaseController(ShowcaseController):

    def _build_context(self):
        # 2 against 1: two thirds and one third, not "two columns wide".
        return {"wide": 2, "narrow": 1,
                "commentary": "The migration is the whole story this quarter. "
                              "Revenue came in 2.0% above budget and operating "
                              "income 0.8% above, but guidance is withdrawn "
                              "and the covenant test moves to FY26 Q2.",
                "figures": "Revenue $38,549m\nOperating income $5,748m\n"
                           "Net debt $8,185m"}

    def _validate_context(self, d):
        """Spans are positive integers, and they differ -- a showcase of a
        ratio needs two different numbers to show one."""
        assert_all_drawn("column", d,
                         [("wide", ("narrow", "commentary", "figures"))])
        for key in ("wide", "narrow"):
            assert isinstance(d[key], int) and d[key] >= 1, \
                (f"column: {key} span is {d[key]!r}; flex-grow below 1 "
                 f"collapses the cell")
        assert d["wide"] != d["narrow"], \
            ("column: both spans are equal, which shows nothing about a "
             "parameter whose only job is to make cells differ")

if __name__ == "__main__":
    print(ColumnShowcaseController().build())
