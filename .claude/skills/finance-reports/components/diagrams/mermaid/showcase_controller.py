"""Showcase controller for the `mermaid` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

It accepts EITHER form: mermaid(code="...") or a {% call %} block.

THE DIAGRAM SOURCE IS WHITESPACE-SENSITIVE and goes into a <pre>, so
indenting it to match the surrounding template breaks it. The block form is
the honest one here: it keeps the source flush left where Mermaid needs it,
and it renders at view time in the browser rather than at build time, so a
syntax error appears as an unrendered block on the page and never as a build
failure.
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


class MermaidShowcaseController(ShowcaseController):

    def _build_context(self):
        # Passed as an argument rather than a block so the source can be kept
        # flush left in Python, where the surrounding indentation is not part
        # of the string.
        return {"code": "\n".join([
            "flowchart LR",
            "  A[Filing] --> B[Controller]",
            "  B --> C{Assertions pass?}",
            "  C -->|no| D[Build stops]",
            "  C -->|yes| E[View]",
            "  E --> F[Report]",
        ])}

    def _validate_context(self, d):
        """The source declares a diagram type on its first line.

        Mermaid renders in the BROWSER, so a bad diagram is not a build
        failure -- it is a blank block on a page that otherwise looks fine.
        This is the only check available before that."""
        assert_all_drawn("mermaid", d, [("code", ())])
        first = d["code"].splitlines()[0].strip()
        kinds = ("flowchart", "graph", "sequenceDiagram", "classDiagram",
                 "stateDiagram", "erDiagram", "gantt", "pie", "journey")
        assert first.startswith(kinds), \
            (f"mermaid: the source opens with {first!r}, which names no "
             f"diagram type; it would render as an empty block in the page "
             f"and never fail the build")
        assert not d["code"].startswith((" ", "\t")), \
            "mermaid: the source is indented; the first line must be flush left"

if __name__ == "__main__":
    print(MermaidShowcaseController().build())
