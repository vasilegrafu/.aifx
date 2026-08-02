"""Showcase controller for the `earnings-surprise` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {metric:str, consensus:str, actual:str, surprise:str, tone:good|bad|neutral}

TONE IS NOT THE SIGN OF THE SURPRISE. Beating on revenue while
missing on margin is two different tones in one table, and a miss on capex can
be good news. The caller decides; the component colours.
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


class EarningsSurpriseShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"metric": "Revenue", "consensus": "$10.1B", "actual": "$10.3B",
             "surprise": "+2.0%", "tone": "good"},
            {"metric": "Gross margin", "consensus": "51.2%", "actual": "49.5%",
             "surprise": "-170 bps", "tone": "bad"},
            {"metric": "EPS", "consensus": "$0.84", "actual": "$0.87",
             "surprise": "+3.6%", "tone": "good"},
            {"metric": "Capital expenditure", "consensus": "$420m",
             "actual": "$361m", "surprise": "-14.0%",
             "tone": "good"},
            {"metric": "Headcount", "consensus": "27,100", "actual": "27,140",
             "surprise": "+0.1%", "tone": "neutral"},
        ]
        return {"rows": rows}

    def _validate_context(self, d):
        """`tone` is one of three, and the table shows all three.

        Note the capex row: a NEGATIVE surprise carrying a GOOD tone. That is
        the case the component exists for, and a showcase without it teaches
        that tone tracks sign."""
        rows = d["rows"]
        assert_rows("earnings-surprise", "rows", rows,
                    ("metric", "consensus", "actual", "surprise", "tone"))
        for i, r in enumerate(rows):
            assert_enum("earnings-surprise", f"rows[{i}].tone", r["tone"],
                        {"good", "bad", "neutral"})
        seen = {r["tone"] for r in rows}
        assert seen == {"good", "bad", "neutral"}, \
            f"earnings-surprise: shows {sorted(seen)}; all three tones should appear"

        contrary = [r for r in rows
                    if r["surprise"].startswith("-") and r["tone"] == "good"]
        assert contrary, \
            ("earnings-surprise: every negative surprise is toned bad, which "
             "teaches that tone tracks sign. It does not -- a capex miss is "
             "good news, and this showcase should say so")

if __name__ == "__main__":
    print(EarningsSurpriseShowcaseController().build())
