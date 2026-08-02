"""Showcase controller for the `toc` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    entries[] {id:str, label:str}

THE TOC TAKES THE SAME LIST THE REPORT RENDERS FROM. That is the
whole design: in a hand-written document the contents drift from the document
the moment a section is renamed, and here they cannot, because one list feeds
both. This showcase renders the sections from `entries` for exactly that
reason -- if it kept a second copy it would be demonstrating the bug.
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


class TocShowcaseController(ShowcaseController):

    def _build_context(self):
        # ONE list. It feeds the table of contents and the sections below it.
        return {"entries": [
            {"id": "sec-summary", "label": "Executive summary"},
            {"id": "sec-results", "label": "FY25 Q2 results"},
            {"id": "sec-valuation", "label": "Valuation"},
            {"id": "sec-risks", "label": "Risks"},
        ]}

    def _validate_context(self, d):
        """Ids and labels distinct, and every id usable as a fragment."""
        assert_all_drawn("toc", d, [("entries", ())])
        assert_rows("toc", "entries", d["entries"], ("id", "label"), 2)
        assert_labels("toc", "ids", [e["id"] for e in d["entries"]])
        assert_labels("toc", "labels", [e["label"] for e in d["entries"]])
        for e in d["entries"]:
            assert e["id"].replace("-", "").isalnum(), \
                (f"toc: id {e['id']!r} is not usable as a fragment; every "
                 f"entry is a link")

if __name__ == "__main__":
    print(TocShowcaseController().build())
