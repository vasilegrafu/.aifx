"""Showcase controller for the `numbered` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items: str[]   -- POSITIONAL AND REQUIRED, numbered(items)

NUMBERED IS FOR SEQUENCE THAT MATTERS TO THE ARGUMENT, not for
procedure -- that is `steps`. The numbers here are a claim that this order is
the right one, which is worth making only when it is.
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


class NumberedShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"items": [
            "Guidance was withdrawn, so no forward figure in this report is "
            "the company's.",
            "The estimates that replace it are the analyst's own, built from "
            "the FY25 Q2 filing.",
            "They assume the migration completes in FY26 Q3, one quarter "
            "later than last stated.",
            "If it slips again, the covenant test at FY26 Q2 becomes the "
            "binding constraint rather than the margin.",
        ]}

    def _validate_context(self, d):
        """Distinct, non-empty items."""
        assert_all_drawn("numbered", d, [("items", ())])
        assert_labels("numbered", "items", d["items"])

if __name__ == "__main__":
    print(NumberedShowcaseController().build())
