"""Showcase controller for the `quote` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

It accepts EITHER form: quote(text=..., source=...) or a {% call %} block.
`source` is optional and drops the footer when empty.

AN UNATTRIBUTED PULL QUOTE IS THE REPORT'S OWN VOICE IN LARGER TYPE.
That is a legitimate use -- it is how a report emphasises its own conclusion --
but it is a different thing from quoting somebody, and the two look identical
at a glance. Both are shown below so the difference is visible.
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


class QuoteShowcaseController(ShowcaseController):

    def _build_context(self):
        return {
            "text": "We are withdrawing full-year guidance until the platform "
                    "migration review concludes. We do not expect to reissue "
                    "it before the second quarter.",
            "source": "Chief Financial Officer, FY26 Q1 earnings call, "
                      "28 January 2026",
            "own": "The withdrawal, not the quarter, is the finding.",
        }

    def _validate_context(self, d):
        """An attributed quote names a person or a document and a date."""
        assert_all_drawn("quote", d, [("text", ("source", "own"))])
        assert len(d["source"].split()) >= 4, \
            (f"quote: source {d['source']!r} is too thin to attribute "
             f"anything; a reader has to be able to go and check it")
        assert any(ch.isdigit() for ch in d["source"]), \
            ("quote: source carries no date; an undated quotation cannot be "
             "placed against the events around it")

if __name__ == "__main__":
    print(QuoteShowcaseController().build())
