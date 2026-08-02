"""Showcase controller for the `expected-value` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {scenario:str, tone:good|neutral|bad, probability:str, target:str, ret:str, weighted:str}

EVERY FIGURE IN THIS COMPONENT IS A STRING and none of them is
checked against any other. The probabilities can sum to 90%, the weighted
column can disagree with probability x return, and the total can be anything
at all -- it renders, and it looks like arithmetic. All six columns here are
computed from the price and the three targets, and the validator recomputes
them from the rendered strings.
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


class ExpectedValueShowcaseController(ShowcaseController):

    def _build_context(self):
        # One price, three targets. Everything else follows.
        price = 118.40
        scenarios = [
            ("Bull", "good", 25, 165.0,
             "Migration lands on time; net retention back above 110%"),
            ("Base", "neutral", 55, 132.0,
             "Migration slips one quarter; retention flat at 104%"),
            ("Bear", "bad", 20, 84.0,
             "Covenant test failed at FY26 Q2; equity raise at a discount"),
        ]
        rows, total = [], 0.0
        for scenario, tone, prob, target, _ in scenarios:
            ret = 100 * (target / price - 1)
            weighted = prob / 100 * ret
            total += weighted
            rows.append({"scenario": scenario, "tone": tone,
                         "probability": f"{prob}%",
                         "target": f"${target:,.0f}",
                         "ret": f"{ret:+.1f}%",
                         "weighted": f"{weighted:+.1f}%"})
        return {"rows": rows, "price": price, "total": f"{total:+.1f}%"}

    def _validate_context(self, d):
        """Probabilities sum to 100, each return follows from the price and
        the target, each weighted cell is probability x return, and the total
        is their sum -- all read back out of the strings that render."""
        assert_rows("expected-value", "rows", d["rows"],
                    ("scenario", "tone", "probability", "target", "ret",
                     "weighted"), 2)
        assert_all_drawn("expected-value", d, [("rows", ("price", "total"))])
        assert_labels("expected-value", "scenarios",
                      [r["scenario"] for r in d["rows"]])

        probabilities, weighted_sum = 0, 0.0
        for r in d["rows"]:
            assert_enum("expected-value", f"{r['scenario']!r}.tone", r["tone"],
                        {"good", "neutral", "bad"})
            prob = float(r["probability"].rstrip("%"))
            target = float(r["target"].lstrip("$").replace(",", ""))
            ret = float(r["ret"].rstrip("%"))
            weighted = float(r["weighted"].rstrip("%"))
            probabilities += prob
            weighted_sum += weighted

            expected_ret = 100 * (target / d["price"] - 1)
            assert abs(expected_ret - ret) < 0.05, \
                (f"expected-value: {r['scenario']!r} shows {r['ret']} from "
                 f"{r['target']} against a price of {d['price']}, but that is "
                 f"{expected_ret:+.1f}%")
            assert abs(prob / 100 * ret - weighted) < 0.05, \
                (f"expected-value: {r['scenario']!r} weights {r['ret']} at "
                 f"{r['probability']} and prints {r['weighted']}, but that is "
                 f"{prob / 100 * ret:+.1f}%")

        assert abs(probabilities - 100) < 0.01, \
            (f"expected-value: probabilities sum to {probabilities}%, not "
             f"100%; the tfoot prints 100% regardless")
        total = float(d["total"].rstrip("%"))
        assert abs(weighted_sum - total) < 0.05, \
            (f"expected-value: weighted column sums to {weighted_sum:+.1f}% "
             f"but the total row prints {d['total']}")

if __name__ == "__main__":
    print(ExpectedValueShowcaseController().build())
