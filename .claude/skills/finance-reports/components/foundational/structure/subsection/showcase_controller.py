"""Showcase controller for the `subsection` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    subsection(id, heading)   -- BOTH POSITIONAL AND REQUIRED

IT IS `section` AT ONE LEVEL DOWN -- the same <section id> with an
<h3> instead of an <h2>. Nesting is by CALLING it inside a section, not by any
argument, so a subsection called at top level produces an h3 with no h2 above
it and a heading outline with a hole in it.
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


class SubsectionShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"parent": {"id": "sec-results", "label": "FY25 Q2 results"},
                "children": [
                    {"id": "sub-revenue", "label": "Revenue and mix"},
                    {"id": "sub-margin", "label": "Margin"},
                ]}

    def _validate_context(self, d):
        """Child ids are distinct from each other and from the parent."""
        assert_all_drawn("subsection", d, [("parent", ("children",))])
        assert_rows("subsection", "children", d["children"], ("id", "label"), 2)
        ids = [d["parent"]["id"]] + [x["id"] for x in d["children"]]
        assert_labels("subsection", "ids", ids)

if __name__ == "__main__":
    print(SubsectionShowcaseController().build())
