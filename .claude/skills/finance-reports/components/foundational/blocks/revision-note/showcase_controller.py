"""Showcase controller for the `revision-note` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    (no data header — the note text arrives as a {% call %} block)

THIS COMPONENT TAKES A BLOCK, NOT DATA. `rev` is the only argument;
the note itself is `caller()`, which is why component.html.j2 carries no
{# data: #} header. The context here supplies only the revision labels.
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


class RevisionNoteShowcaseController(ShowcaseController):

    def _build_context(self):
        # Only the labels. The note bodies are prose and belong in the view,
        # which is where the {% call %} blocks are written.
        return {"minor": "v3.1", "major": "v3.0"}

    def _validate_context(self, d):
        """Both revisions are non-empty and distinct."""
        assert_all_drawn("revision-note", d, [("minor", ("major",))])
        assert_labels("revision-note", "revisions",
                      [d["minor"], d["major"]])

if __name__ == "__main__":
    print(RevisionNoteShowcaseController().build())
