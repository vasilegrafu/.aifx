"""Showcase controller for the `timeline` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {state:done|current|todo, when:str, title:str, detail:str}

STATES ARE done, current AND todo. blocks.css carries a rule for done and
for current; "todo" is deliberately unstyled and is the default appearance, so
a milestone that has not started looks like one. Anything else renders with the
plain marker and is indistinguishable from a future milestone.
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


class TimelineShowcaseController(ShowcaseController):

    def _build_context(self):
        # Exactly one item is current -- it is what answers "where are we
        # now", and two of them answer nothing.
        items = [
            {"state": "done", "when": "2025-11-19",
             "title": "Coverage initiated",
             "detail": "Buy, price target $132, on the FY25 Q3 filing."},
            {"state": "done", "when": "2026-01-28",
             "title": "Guidance withdrawn",
             "detail": "Management pulled FY26 guidance pending the platform "
                       "migration review."},
            {"state": "current", "when": "2026-02-02",
             "title": "Rating cut to Hold",
             "detail": "Price target reduced to $118. Awaiting the restated "
                       "segment split."},
            {"state": "todo", "when": "2026-08-14",
             "title": "FY26 Q2 results",
             "detail": "First period on the new reporting lines."},
            {"state": "todo", "when": "2026-11-06",
             "title": "Capital markets day",
             "detail": "Expected reset of the medium-term margin target."},
        ]
        return {"items": items}

    def _validate_context(self, d):
        """States are ones the stylesheet knows, dates run forward, and exactly
        one item is current."""
        assert_rows("timeline", "items", d["items"],
                    ("state", "when", "title", "detail"), 2)
        assert_all_drawn("timeline", d, [("items", ())])
        assert_labels("timeline", "titles", [i["title"] for i in d["items"]])
        for it in d["items"]:
            assert_enum("timeline", f"{it['title']!r}.state", it["state"],
                        {"done", "current", "todo"})
        dates = [i["when"] for i in d["items"]]
        assert dates == sorted(dates), \
            ("timeline: items are not in date order; the component draws a "
             "line down the page and the reader takes it as the sequence")
        current = [i for i in d["items"] if i["state"] == "current"]
        assert len(current) == 1, \
            (f"timeline: {len(current)} items marked current; the highlight "
             f"is meant to answer 'where are we now'")

if __name__ == "__main__":
    print(TimelineShowcaseController().build())
