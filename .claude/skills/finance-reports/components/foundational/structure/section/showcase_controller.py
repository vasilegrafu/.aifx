"""Showcase controller for the `section` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    section(id, heading)   -- BOTH POSITIONAL AND REQUIRED

THE id IS WHAT THE TABLE OF CONTENTS POINTS AT, which is why `toc`
takes the same list the report renders from -- the two cannot disagree if they
come from one source. A section whose id is changed without the TOC's is a
link that resolves to nothing, and nothing raises.
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


class SectionShowcaseController(ShowcaseController):

    def _build_context(self):
        # The list a report would pass to BOTH section() and toc(), which is
        # the arrangement that keeps them in step.
        return {"sections": [
            {"id": "sec-summary", "label": "Executive summary"},
            {"id": "sec-results", "label": "FY25 Q2 results"},
        ]}

    def _validate_context(self, d):
        """Ids and labels distinct, ids usable as fragments."""
        assert_all_drawn("section", d, [("sections", ())])
        assert_rows("section", "sections", d["sections"], ("id", "label"), 2)
        assert_labels("section", "ids", [s["id"] for s in d["sections"]])
        assert_labels("section", "labels", [s["label"] for s in d["sections"]])
        for s in d["sections"]:
            assert s["id"].replace("-", "").isalnum(), \
                f"section: id {s['id']!r} is not usable as a fragment"

if __name__ == "__main__":
    print(SectionShowcaseController().build())
