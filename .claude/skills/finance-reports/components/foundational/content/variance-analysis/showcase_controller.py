"""Showcase controller for the `variance-analysis` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {line:str, budget:str, actual:str, variance:str, pct:str, verdict:favourable|adverse|neutral}  total_row? {label, cells}

FAVOURABLE IS NOT THE SAME AS POSITIVE, and this is the component
where that distinction lives. Revenue above budget is favourable; cost above
budget is adverse, with the same sign on the variance. Nothing in the macro
knows which lines are costs, so the verdict is the author's claim and the
validator below checks it against a declared direction for each line.

The macro maps favourable -> badge-good and adverse -> badge-bad; ANY other
verdict falls through to badge-info, so a typo renders as a neutral badge
carrying the typo as its text.
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


class VarianceAnalysisShowcaseController(ShowcaseController):

    def _build_context(self):
        # `better` says which direction is good for each line, which is the
        # fact the macro cannot know and the verdict depends on entirely.
        lines = [
            ("Revenue", 37800, 38549, "higher"),
            ("Cost of sales", 18900, 19468, "lower"),
            ("Operating expenses", 13200, 13333, "lower"),
            ("Operating income", 5700, 5748, "higher"),
        ]
        rows = []
        for line, budget, actual, better in lines:
            delta = actual - budget
            favourable = (delta > 0) if better == "higher" else (delta < 0)
            rows.append({
                "line": line,
                "budget": f"{budget:,}",
                "actual": f"{actual:,}",
                # Accounting parentheses for a variance that hurts.
                "variance": (f"{delta:+,}" if favourable
                             else f"({abs(delta):,})"),
                "pct": f"{100 * delta / budget:+.1f}%",
                "verdict": "favourable" if favourable else "adverse",
                "better": better,
            })
        total_row = {"label": "Net income",
                     "cells": ["4,760", "5,136", "+376", "+7.9%", ""]}
        return {"rows": rows, "total_row": total_row}

    def _validate_context(self, d):
        """The variance follows from budget and actual, the percentage follows
        from the variance, and the verdict follows from the direction that is
        good for that line."""
        assert_rows("variance-analysis", "rows", d["rows"],
                    ("line", "budget", "actual", "variance", "pct", "verdict",
                     "better"), 2)
        assert_all_drawn("variance-analysis", d, [("rows", ("total_row",))])
        assert_labels("variance-analysis", "lines",
                      [r["line"] for r in d["rows"]])

        def number(text):
            text = text.replace(",", "").replace("%", "").replace("+", "")
            if text.startswith("(") and text.endswith(")"):
                return -float(text[1:-1])
            return float(text)

        for r in d["rows"]:
            assert_enum("variance-analysis", f"{r['line']!r}.verdict",
                        r["verdict"], {"favourable", "adverse", "neutral"})
            assert_enum("variance-analysis", f"{r['line']!r}.better",
                        r["better"], {"higher", "lower"})
            budget, actual = number(r["budget"]), number(r["actual"])
            delta = actual - budget

            assert abs(abs(number(r["variance"])) - abs(delta)) < 0.51, \
                (f"variance-analysis: {r['line']!r} runs {budget:,} to "
                 f"{actual:,} but prints a variance of {r['variance']}")
            assert abs(number(r["pct"]) - 100 * delta / budget) < 0.05, \
                (f"variance-analysis: {r['line']!r} varies by {delta:+,} on "
                 f"{budget:,}, which is {100 * delta / budget:+.1f}%, not "
                 f"{r['pct']}")

            favourable = (delta > 0) if r["better"] == "higher" else (delta < 0)
            expected = "favourable" if favourable else "adverse"
            assert r["verdict"] == expected, \
                (f"variance-analysis: {r['line']!r} is {delta:+,} against "
                 f"budget and {r['better']} is better, so it is {expected}, "
                 f"not {r['verdict']}")

        assert len(d["total_row"]["cells"]) == 5, \
            (f"variance-analysis: total_row has "
             f"{len(d['total_row']['cells'])} cells against the 5 body "
             f"columns; the tfoot would sit under the wrong headings")

if __name__ == "__main__":
    print(VarianceAnalysisShowcaseController().build())
