"""Showcase controller for the `lead` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    lead(text="")   -- also accepts a {% call %} block

THERE IS ONE LEAD PER DOCUMENT. It is the emphasised opening of the
executive summary, and a second one is just large body text -- the emphasis
comes from being the only paragraph set that way, so using it twice removes
the reason it works.
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


class LeadShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"text": "Rating cut to Hold. The migration, not the quarter, "
                        "is the finding: revenue beat budget by 2.0% and "
                        "operating income by 0.8%, but guidance is withdrawn, "
                        "net retention has fallen for four consecutive "
                        "quarters, and the leverage covenant is next tested "
                        "in eight months."}

    def _validate_context(self, d):
        """A lead is a paragraph, not a sentence fragment or an essay."""
        assert_all_drawn("lead", d, [("text", ())])
        words = len(d["text"].split())
        assert 20 <= words <= 90, \
            (f"lead: {words} words; below 20 it carries no summary and above "
             f"90 the emphasis has nothing left to emphasise")

if __name__ == "__main__":
    print(LeadShowcaseController().build())
