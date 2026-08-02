"""Showcase controller for the `appendix` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    appendix(id, heading)   -- BOTH POSITIONAL AND REQUIRED

`id` AND `heading` HAVE NO DEFAULTS, so a call missing either raises
rather than rendering a section with a blank heading. That is the right
behaviour and it is worth knowing about: most macros in this library render
empty instead.

The id is a link target, so it has to be unique across the whole document --
not merely across the appendices.
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


class AppendixShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"items": [
            {"id": "app-a", "heading": "Peer set and selection criteria"},
            {"id": "app-b", "heading": "Reconciliation to reported figures"},
        ]}

    def _validate_context(self, d):
        """Ids are distinct and usable as URL fragments."""
        assert_all_drawn("appendix", d, [("items", ())])
        assert_rows("appendix", "items", d["items"], ("id", "heading"), 2)
        assert_labels("appendix", "ids", [i["id"] for i in d["items"]])
        assert_labels("appendix", "headings",
                      [i["heading"] for i in d["items"]])
        for item in d["items"]:
            assert item["id"].replace("-", "").isalnum(), \
                (f"appendix: id {item['id']!r} is not usable as a fragment; "
                 f"the table of contents links to it")

if __name__ == "__main__":
    print(AppendixShowcaseController().build())
