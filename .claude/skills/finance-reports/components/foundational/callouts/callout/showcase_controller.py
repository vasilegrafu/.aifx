"""Showcase controller for the `callout` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

FOUR TYPES ARE STYLED: note, warning, decision, risk. The class is the
type string with nothing in between, so callouts.css is the whole contract --
`aside.note`, `aside.warning`, `aside.decision`, `aside.risk` and nothing else.
A fifth type renders as an unstyled <aside>, which reads as body text.
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


class CalloutShowcaseController(ShowcaseController):

    def _build_context(self):
        # The four the stylesheet styles, in the order they escalate.
        return {"types": ["note", "warning", "decision", "risk"]}

    def _validate_context(self, d):
        """Only the four types callouts.css has a rule for."""
        assert_all_drawn("callout", d, [("types", ())])
        assert_labels("callout", "types", d["types"])
        for t in d["types"]:
            assert_enum("callout", "types", t,
                        {"note", "warning", "decision", "risk"})

if __name__ == "__main__":
    print(CalloutShowcaseController().build())
