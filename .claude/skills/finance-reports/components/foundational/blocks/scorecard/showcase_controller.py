"""Showcase controller for the `scorecard` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {criterion:str, weight:str, score:num, note:str} -- score out of `scale`

THE TOTAL IS FREE TEXT. `total` is printed as given and the macro
never checks it against the rows, so a scorecard whose weighted total does not
follow from its own weights and scores renders happily. The total here is
computed from the rows below, and the validator recomputes it.

`weight` IS ALSO FREE TEXT -- it is printed, not used in any arithmetic. The
weights are parsed back out below purely to check they sum to 100%.
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


class ScorecardShowcaseController(ShowcaseController):

    def _build_context(self):
        # 0.30*4 + 0.25*3 + 0.20*5 + 0.15*2 + 0.10*4 = 3.65
        rows = [
            {"criterion": "Balance sheet", "weight": "30%", "score": 4,
             "note": "Net debt/EBITDA 1.24x; no maturity before FY28"},
            {"criterion": "Revenue quality", "weight": "25%", "score": 3,
             "note": "68% recurring, but net retention fell to 104%"},
            {"criterion": "Competitive position", "weight": "20%", "score": 5,
             "note": "Share gains in all four regions for six quarters"},
            {"criterion": "Capital allocation", "weight": "15%", "score": 2,
             "note": "Two write-downs on acquisitions since FY23"},
            {"criterion": "Governance", "weight": "10%", "score": 4,
             "note": "Independent chair; no related-party transactions"},
        ]
        weighted = sum(int(r["weight"].rstrip("%")) / 100 * r["score"]
                       for r in rows)
        return {"rows": rows, "scale": 5, "total": f"{weighted:.2f} / 5"}

    def _validate_context(self, d):
        """Weights sum to 100%, scores fit the scale, and the printed total is
        the one the rows produce."""
        assert_rows("scorecard", "rows", d["rows"],
                    ("criterion", "weight", "score", "note"), 2)
        assert_all_drawn("scorecard", d, [("rows", ("scale", "total"))])
        assert_labels("scorecard", "criteria",
                      [r["criterion"] for r in d["rows"]])
        assert_numbers("scorecard", "scores", [r["score"] for r in d["rows"]])
        for r in d["rows"]:
            assert 0 <= r["score"] <= d["scale"], \
                (f"scorecard: {r['criterion']!r} scores {r['score']} out of "
                 f"{d['scale']}; the rating bar computes past 100% and leaves "
                 f"its track")

        weights = [int(r["weight"].rstrip("%")) for r in d["rows"]]
        assert sum(weights) == 100, \
            (f"scorecard: weights sum to {sum(weights)}%, not 100%; the "
             f"weighted total below is then an average of nothing in "
             f"particular")
        weighted = sum(w / 100 * r["score"] for w, r in zip(weights, d["rows"]))
        assert d["total"].startswith(f"{weighted:.2f}"), \
            (f"scorecard: rows produce {weighted:.2f} but the total row prints "
             f"{d['total']!r}; the macro prints it as given and checks nothing")

if __name__ == "__main__":
    print(ScorecardShowcaseController().build())
