"""Showcase controller for the `facts` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {term:str, value:str}

THIS TOOK NAMED KEYS FOR A REASON, and the component header says it:
it used to take (term, desc) tuples, and a two-tuple is the shape most likely
to be filled in backwards and least likely to complain. Transposed, it renders
perfectly -- every label in the value column and every value in the label
column -- and nothing anywhere raises.
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


class FactsShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"rows": [
            {"term": "Ticker", "value": "NWND"},
            {"term": "Rating", "value": "Hold, cut from Buy on 2 February 2026"},
            {"term": "Price", "value": "$118.40"},
            {"term": "Price target", "value": "$118"},
            {"term": "Shares outstanding", "value": "338.2m"},
            {"term": "Market capitalisation", "value": "$40,043m"},
            {"term": "As of", "value": "FY25 Q2, filed 24 July 2026"},
        ]}

    def _validate_context(self, d):
        """Terms are distinct, and no term looks like a value.

        The transposition this component was reshaped to prevent is still
        possible one row at a time; a term that is a bare number is the
        signature of it."""
        assert_all_drawn("facts", d, [("rows", ())])
        assert_rows("facts", "rows", d["rows"], ("term", "value"), 2)
        assert_labels("facts", "terms", [r["term"] for r in d["rows"]])
        for r in d["rows"]:
            head = r["term"].lstrip("$").replace(",", "").replace(".", "")
            assert not head.isdigit(), \
                (f"facts: term {r['term']!r} is a number; the term is the "
                 f"LABEL, and a transposed row renders perfectly")

        # A cover block is where a wrong number does the most damage: it is
        # the part everyone reads and nobody recomputes.
        by_term = {r["term"]: r["value"] for r in d["rows"]}
        price = float(by_term["Price"].lstrip("$"))
        shares = float(by_term["Shares outstanding"].rstrip("m"))
        cap = float(by_term["Market capitalisation"]
                    .lstrip("$").rstrip("m").replace(",", ""))
        assert abs(shares * price - cap) < 1.0, \
            (f"facts: {shares}m shares at {by_term['Price']} is "
             f"${shares * price:,.0f}m, not "
             f"{by_term['Market capitalisation']}")

if __name__ == "__main__":
    print(FactsShowcaseController().build())
