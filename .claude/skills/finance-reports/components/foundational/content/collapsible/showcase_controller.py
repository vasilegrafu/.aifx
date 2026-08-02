"""Showcase controller for the `collapsible` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    collapsible(summary="")   -- the always-visible line

THE SUMMARY MUST SAY WHAT IS INSIDE. It is the only part a reader
sees before deciding, so "Details" or "More information" hides the content
behind a line that carries none of it. Collapsing is for length, never for
inconvenience -- a caveat that changes the conclusion does not belong in here.
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


class CollapsibleShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"method": "How the WACC of 9.0% was built",
                "restated": "Which FY24 figures were restated, and why"}

    def _validate_context(self, d):
        """Both summaries describe their contents rather than announcing that
        contents exist."""
        assert_all_drawn("collapsible", d, [("method", ("restated",))])
        vague = {"details", "more", "more information", "read more", "info"}
        for key, summary in d.items():
            assert summary.strip().lower() not in vague, \
                (f"collapsible: {key} summary is {summary!r}; the summary is "
                 f"all a reader has when deciding whether to open it")
            assert len(summary.split()) >= 4, \
                f"collapsible: {key} summary is too short to describe anything"

if __name__ == "__main__":
    print(CollapsibleShowcaseController().build())
