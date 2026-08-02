"""Showcase controller for the `references` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {id:str, text:str}

UNLIKE FOOTNOTES, REFERENCES CARRY THEIR OWN ID -- so a reference can
be cited from anywhere and inserting one in the middle does not renumber the
citations. That is the whole difference between the two components, and it is
why a source that is cited more than once belongs here rather than there.
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


class ReferencesShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"items": [
            {"id": "ref-10k",
             "text": "Annual report on Form 10-K for the year ended "
                     "31 December 2025, filed 14 February 2026."},
            {"id": "ref-q2",
             "text": "Quarterly report on Form 10-Q for the period ended "
                     "30 June 2026, filed 24 July 2026."},
            {"id": "ref-call",
             "text": "FY26 Q1 earnings call transcript, 28 January 2026."},
        ]}

    def _validate_context(self, d):
        """Ids are distinct and usable as fragments; every entry is dated."""
        assert_all_drawn("references", d, [("items", ())])
        assert_rows("references", "items", d["items"], ("id", "text"), 2)
        assert_labels("references", "ids", [i["id"] for i in d["items"]])
        assert_labels("references", "texts", [i["text"] for i in d["items"]])
        for item in d["items"]:
            assert item["id"].replace("-", "").isalnum(), \
                f"references: id {item['id']!r} is not usable as a fragment"
            assert any(ch.isdigit() for ch in item["text"]), \
                (f"references: {item['id']!r} carries no date; a reference a "
                 f"reader cannot locate in time is not one")

if __name__ == "__main__":
    print(ReferencesShowcaseController().build())
