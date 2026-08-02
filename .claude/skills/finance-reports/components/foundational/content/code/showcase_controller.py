"""Showcase controller for the `code` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    code(lang="")   -- lang becomes data-lang on the <code>

THE BODY MUST BE WRAPPED IN {% raw %}. Jinja renders the block before
the macro sees it, so a sample containing {{ or {% is executed rather than
printed -- which is exactly the sample a report about templates wants to show.
Both sections below are raw-wrapped.
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


class CodeShowcaseController(ShowcaseController):

    def _build_context(self):
        # Nothing but the language tags. The samples are prose and live in
        # the view, inside {% raw %} so Jinja prints them instead of running
        # them.
        return {"langs": ["python", "jinja"]}

    def _validate_context(self, d):
        """Distinct, non-empty language tags."""
        assert_all_drawn("code", d, [("langs", ())])
        assert_labels("code", "langs", d["langs"])

if __name__ == "__main__":
    print(CodeShowcaseController().build())
