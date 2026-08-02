"""Showcase controller for the `change-history` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {version:str, date:str, author:str, change:str}

NEWEST FIRST. A revision log read top-down should answer "what
changed most recently" in one line; the reader who wants the beginning can
scroll. The `change` column says what changed, not that something did --
"updated figures" is what an empty row looks like when somebody felt obliged
to fill it.
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


class ChangeHistoryShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"version": "3.2", "date": "2026-07-28", "author": "A. Okonkwo",
             "change": "FY25 Q2 actuals replace estimates; DCF WACC 8.6% -> 9.0%"},
            {"version": "3.1", "date": "2026-05-14", "author": "A. Okonkwo",
             "change": "Segment split restated to the new reporting lines"},
            {"version": "3.0", "date": "2026-02-02", "author": "M. Halvorsen",
             "change": "Rating cut to Hold; price target $132 -> $118"},
            {"version": "2.4", "date": "2025-11-19", "author": "R. Delacroix",
             "change": "Disclosure block added for the convertible holding"},
        ]
        return {"rows": rows}

    def _validate_context(self, d):
        """Versions are distinct and dates run newest first.

        A log out of order is not a render error -- it just quietly stops
        being a log."""
        assert_rows("change-history", "rows", d["rows"],
                    ("version", "date", "author", "change"), 2)
        assert_all_drawn("change-history", d, [("rows", ())])
        assert_labels("change-history", "versions",
                      [r["version"] for r in d["rows"]])
        dates = [r["date"] for r in d["rows"]]
        assert dates == sorted(dates, reverse=True), \
            ("change-history: rows are not newest-first; the top line is what "
             "a reader takes as the current state")

if __name__ == "__main__":
    print(ChangeHistoryShowcaseController().build())
