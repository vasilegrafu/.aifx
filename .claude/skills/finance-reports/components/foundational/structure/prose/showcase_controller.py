"""Showcase controller for the `prose` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    prose(text="")   -- also accepts a {% call %} block

BOTH CALL FORMS EXIST because they solve different problems: the
`text=` form is what a loop over strings produces, and the {% call %} form is
what you need when the paragraph contains other components or markup. The
argument form escapes its content; the block form does not.
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


class ProseShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"paragraphs": [
            "Revenue of $38,549m was 2.0% above budget, with the beat "
            "concentrated in Platform. Services and Licensing both came in "
            "within half a point of plan.",
            "Gross margin fell 2.0 points to 49.5%. The mix, not the rate, "
            "explains it: Platform carries the lowest margin of the three "
            "segments and grew fastest.",
        ]}

    def _validate_context(self, d):
        """Distinct paragraphs, each a real one."""
        assert_all_drawn("prose", d, [("paragraphs", ())])
        assert_labels("prose", "paragraphs", d["paragraphs"])
        for p in d["paragraphs"]:
            assert len(p.split()) >= 10, \
                f"prose: {p[:40]!r} is too short to be a paragraph"

if __name__ == "__main__":
    print(ProseShowcaseController().build())
