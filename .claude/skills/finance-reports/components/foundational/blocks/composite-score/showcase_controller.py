"""Showcase controller for the `composite-score` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    inputs[] {component:str, coefficient:num, value:num, contribution:num}   bands[] {label:str, range:str, tone:good|warn|bad}

SHOW THE INPUTS, NOT JUST THE NUMBER, as the component header says.
This showcase makes the header's point with real arithmetic: of the 3.99 total,
1.72 comes from one term -- 43% of an Altman Z-score that moves with the share
price rather than with the business.

TONES ARE good|warn|bad, for the outer band AND for each pill on the scale.
The two read the same three tokens, so a band cannot be styled one way in the
summary and another in the scale beneath it.
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


class CompositeScoreShowcaseController(ShowcaseController):

    def _build_context(self):
        # Altman Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5.
        # Contributions are the products, and they sum to 3.9939 -> 3.99.
        inputs = [
            {"component": "Working capital / total assets",
             "coefficient": 1.2, "value": 0.2140, "contribution": 0.2568},
            {"component": "Retained earnings / total assets",
             "coefficient": 1.4, "value": 0.4310, "contribution": 0.6034},
            {"component": "EBIT / total assets",
             "coefficient": 3.3, "value": 0.1490, "contribution": 0.4917},
            {"component": "Market value of equity / total liabilities",
             "coefficient": 0.6, "value": 2.8700, "contribution": 1.7220},
            {"component": "Sales / total assets",
             "coefficient": 1.0, "value": 0.9200, "contribution": 0.9200},
        ]
        bands = [
            {"label": "Distress", "range": "< 1.81", "tone": "bad"},
            {"label": "Grey", "range": "1.81 - 2.99", "tone": "warn"},
            {"label": "Safe", "range": "> 2.99", "tone": "good"},
        ]
        return {"inputs": inputs, "bands": bands,
                "score": 3.99, "band": "Safe", "tone": "good"}

    def _validate_context(self, d):
        """Each contribution is its own coefficient times its own value, the
        contributions sum to the score, and the score falls in the named band.

        A composite score is the one component where the arithmetic is the
        whole claim: a table whose rows do not add to its own total is worse
        than no table, because it looks checked."""
        assert_all_drawn("composite-score", d,
                         [("inputs", ("score", "band", "tone", "bands"))])
        assert_rows("composite-score", "inputs", d["inputs"],
                    ("component", "coefficient", "value", "contribution"), 2)
        assert_labels("composite-score", "input names",
                      [i["component"] for i in d["inputs"]])
        for i in d["inputs"]:
            assert_numbers("composite-score", i["component"],
                           [i["coefficient"], i["value"], i["contribution"]])
            expected = i["coefficient"] * i["value"]
            assert abs(expected - i["contribution"]) < 0.0005, \
                (f"composite-score: {i['component']!r} shows a contribution of "
                 f"{i['contribution']} but {i['coefficient']} x {i['value']} "
                 f"is {expected:.4f}")
        total = sum(i["contribution"] for i in d["inputs"])
        assert abs(total - d["score"]) < 0.01, \
            (f"composite-score: contributions sum to {total:.4f}, but the "
             f"score printed in the total row is {d['score']}")

        assert_rows("composite-score", "bands", d["bands"],
                    ("label", "range", "tone"), 2)
        labels = [b["label"] for b in d["bands"]]
        assert_labels("composite-score", "band labels", labels)
        assert d["band"] in labels, \
            (f"composite-score: band {d['band']!r} is not one of "
             f"{labels}; the scale would highlight nothing")
        assert_enum("composite-score", "tone", d["tone"],
                    {"good", "bad", "warn"})

if __name__ == "__main__":
    print(CompositeScoreShowcaseController().build())
