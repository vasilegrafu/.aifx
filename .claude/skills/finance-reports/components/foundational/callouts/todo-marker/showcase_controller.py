"""Showcase controller for the `todo-marker` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

It accepts EITHER form: `caller() if caller is defined else text`, so it
works as {% call %} or as todo_marker(text="...").

AN UNRESOLVED TODO IS SUPPOSED TO BE UGLY. It marks something the
report could not establish, and the whole value of the component is that a
reader cannot skim past it. Both call forms are shown below because both
appear in real recipes.
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


class TodoMarkerShowcaseController(ShowcaseController):

    def _build_context(self):
        # Used as a plain argument rather than a block. Both forms render
        # identically; the argument form is what a loop over gaps produces.
        return {"gaps": ["segment split for FY24",
                         "auditor's going-concern wording"]}

    def _validate_context(self, d):
        """Non-empty, distinct gap descriptions."""
        assert_all_drawn("todo-marker", d, [("gaps", ())])
        assert_labels("todo-marker", "gaps", d["gaps"])

if __name__ == "__main__":
    print(TodoMarkerShowcaseController().build())
