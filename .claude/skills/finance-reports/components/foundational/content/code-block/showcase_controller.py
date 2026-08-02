"""Showcase controller for the `code-block` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    code_block(path="", lang="")   -- path titles the frame

`path` IS THE TITLE BAR AND IT SHOULD BE A REAL PATH. The framed form
exists to say where a sample came from; filled with a description instead
("the controller") it becomes a caption, and the reader loses the one thing
the frame was for.
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


class CodeBlockShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"path": "components/foundational/content/roll-forward"
                        "/showcase_controller.py",
                "lang": "python"}

    def _validate_context(self, d):
        """The path looks like a path, and the language is named."""
        assert_all_drawn("code-block", d, [("path", ("lang",))])
        assert "/" in d["path"], \
            (f"code-block: path {d['path']!r} has no separator; the title bar "
             f"is there to say WHERE the sample lives")
        assert d["lang"], "code-block: lang is what colours the sample"

if __name__ == "__main__":
    print(CodeBlockShowcaseController().build())
