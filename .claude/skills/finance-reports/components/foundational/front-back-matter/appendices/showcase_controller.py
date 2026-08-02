"""Showcase controller for the `appendices` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    appendices()   -- no arguments; it wraps `appendix` calls

THIS EXISTS TO RESTART THE NUMBERING. Body sections are numbered and
appendices are lettered, and the wrapper is what separates the two counters --
which means an `appendix` called outside it inherits the body's numbering and
appears as another section.
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


class AppendicesShowcaseController(ShowcaseController):

    def _build_context(self):
        # The wrapper takes no arguments at all; what varies is what goes
        # inside it, so the context describes the appendices it will hold.
        return {"items": [
            {"id": "app-a", "heading": "Peer set and selection criteria"},
            {"id": "app-b", "heading": "Reconciliation to reported figures"},
        ]}

    def _validate_context(self, d):
        """Distinct ids and headings for the appendices inside."""
        assert_all_drawn("appendices", d, [("items", ())])
        assert_rows("appendices", "items", d["items"], ("id", "heading"), 2)
        assert_labels("appendices", "ids", [i["id"] for i in d["items"]])
        assert_labels("appendices", "headings",
                      [i["heading"] for i in d["items"]])

if __name__ == "__main__":
    print(AppendicesShowcaseController().build())
