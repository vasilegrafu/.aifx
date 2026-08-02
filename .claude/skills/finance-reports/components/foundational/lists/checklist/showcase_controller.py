"""Showcase controller for the `checklist` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {state:done|pending|blocked, text:str}

THREE STATES ARE STYLED, and lists.css carries a rule for each:
done renders a tick, pending an open circle, blocked a cross AND turns the
whole line red. Any other state renders with no marker at all, which reads as
an ordinary bullet rather than as an unknown status.
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


class ChecklistShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"items": [
            {"state": "done", "text": "FY25 Q2 figures pulled and reconciled "
                                      "to the filing"},
            {"state": "done", "text": "Peer set refreshed; two companies "
                                      "dropped for a fiscal year change"},
            {"state": "pending", "text": "DCF rebuilt at the revised 9.0% "
                                        "WACC"},
            {"state": "pending", "text": "Compliance review of the rating "
                                        "change"},
            {"state": "blocked", "text": "Segment bridge to the restated FY24 "
                                         "base — the company has not published "
                                         "one"},
        ]}

    def _validate_context(self, d):
        """Every state has a rule in lists.css."""
        assert_all_drawn("checklist", d, [("items", ())])
        assert_rows("checklist", "items", d["items"], ("state", "text"), 2)
        assert_labels("checklist", "texts", [i["text"] for i in d["items"]])
        for item in d["items"]:
            assert_enum("checklist", f"{item['text'][:30]!r}.state",
                        item["state"], {"done", "pending", "blocked"})

if __name__ == "__main__":
    print(ChecklistShowcaseController().build())
