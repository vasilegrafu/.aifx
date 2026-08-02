"""Showcase controller for the `glossary` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    terms[] {id:str, term:str, desc:str}

THE `id` IS A LINK TARGET. It is what the rest of the report points
at, so it has to be stable and unique across the document -- a repeated id
means every link to it lands on whichever came first.
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


class GlossaryShowcaseController(ShowcaseController):

    def _build_context(self):
        terms = [
            {"id": "g-fcf", "term": "Free cash flow",
             "desc": "Cash from operations less capital expenditure. Reported "
                     "before acquisitions, which is why it flatters an "
                     "acquisitive company."},
            {"id": "g-wacc", "term": "WACC",
             "desc": "Weighted average cost of capital — the discount rate a "
                     "DCF applies to future cash flows. A one-point change "
                     "moves this valuation by roughly 14%."},
            {"id": "g-nwc", "term": "Net working capital",
             "desc": "Receivables plus inventory less payables. A rise "
                     "consumes cash even when it accompanies growth."},
            {"id": "g-tsr", "term": "Total shareholder return",
             "desc": "Share price change plus dividends, expressed as a "
                     "compound annual rate over the stated period."},
        ]
        return {"terms": terms}

    def _validate_context(self, d):
        """Ids and terms are both distinct, and the ids are usable in a URL."""
        assert_rows("glossary", "terms", d["terms"], ("id", "term", "desc"), 2)
        assert_all_drawn("glossary", d, [("terms", ())])
        assert_labels("glossary", "ids", [t["id"] for t in d["terms"]])
        assert_labels("glossary", "terms", [t["term"] for t in d["terms"]])
        for t in d["terms"]:
            assert t["id"].replace("-", "").replace("_", "").isalnum(), \
                (f"glossary: id {t['id']!r} is not usable as a fragment; the "
                 f"report links terms by id")

if __name__ == "__main__":
    print(GlossaryShowcaseController().build())
