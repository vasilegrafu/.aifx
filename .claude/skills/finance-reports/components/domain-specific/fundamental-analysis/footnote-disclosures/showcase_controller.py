"""Showcase controller for the `footnote-disclosures` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {num:int, title:str, body:str, flag?:watch} -- anchors at id=note-<num>

THE NUMBERS ARE ANCHOR TARGETS -- `id=note-<num>` -- so they must be
unique and they must match whatever the prose links to. A duplicate silently
makes one of the two links unreachable.
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
    assert_enum, assert_numbers, assert_rows)
from components._showcase_controller import ShowcaseController     # noqa: E402


class FootnoteDisclosuresShowcaseController(ShowcaseController):

    def _build_context(self):
        items = [
            {"num": 1, "title": "Revenue recognition",
             "body": "Distributor sales are recognised on sell-through rather "
                     "than sell-in. A change here would move revenue between "
                     "quarters without changing the year."},
            {"num": 2, "title": "Goodwill",
             "body": "$41.5bn, of which $38.2bn arose on one acquisition in "
                     "2022. No impairment has been recorded.",
             "flag": "watch"},
            {"num": 3, "title": "Share-based compensation",
             "body": "$1.8bn charged in FY25, 4.7% of revenue, excluded from "
                     "the non-GAAP measures management guides to."},
            {"num": 4, "title": "Foundry prepayments",
             "body": "$1.4bn advanced against future capacity, recoverable "
                     "only as wafers.",
             "flag": "watch"},
        ]
        return {"items": items}

    def _validate_context(self, d):
        """Numbers are ANCHOR TARGETS: unique, positive, and in order.

        A duplicate makes `#note-2` resolve to whichever came first, and the
        other reference silently points at the wrong note."""
        items = d["items"]
        assert_rows("footnote-disclosures", "items", items, ("num", "title", "body"))
        nums = [i["num"] for i in items]
        for i, it in enumerate(items):
            assert isinstance(it["num"], int) and it["num"] > 0, \
                (f"footnote-disclosures: items[{i}] num is {it['num']!r}; it "
                 f"becomes id=note-<num> and must be a positive integer")
            if "flag" in it:
                assert_enum("footnote-disclosures", f"items[{i}].flag",
                            it["flag"], {"watch"})
        dupes = sorted({n for n in nums if nums.count(n) > 1})
        assert not dupes, \
            (f"footnote-disclosures: note number(s) {dupes} appear twice; "
             f"#note-{dupes[0] if dupes else 'N'} would resolve to whichever "
             f"came first and the other reference would point at the wrong note")
        assert nums == sorted(nums), \
            f"footnote-disclosures: numbers {nums} are out of order"

if __name__ == "__main__":
    print(FootnoteDisclosuresShowcaseController().build())
