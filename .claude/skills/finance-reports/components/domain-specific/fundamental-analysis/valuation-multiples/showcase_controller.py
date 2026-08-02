"""Showcase controller for the `valuation-multiples` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {multiple:str, current:str, peers:str, history:str, premium:str, verdict:cheap|fair|rich}

THREE REFERENCE POINTS PER ROW -- against peers, against its own
history, and the premium that follows. A multiple quoted alone is a number; a
multiple against two baselines is an argument.
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


class ValuationMultiplesShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"multiple": "EV / EBITDA", "current": "47.9x", "peers": "19.7x",
             "history": "28.4x", "premium": "+143% / +69%", "verdict": "rich"},
            {"multiple": "EV / sales", "current": "8.1x", "peers": "5.2x",
             "history": "6.9x", "premium": "+56% / +17%", "verdict": "rich"},
            {"multiple": "P / E, forward", "current": "31.2x", "peers": "27.8x",
             "history": "34.1x", "premium": "+12% / -9%", "verdict": "fair"},
            {"multiple": "P / book", "current": "4.6x", "peers": "6.1x",
             "history": "5.2x", "premium": "-25% / -12%", "verdict": "cheap"},
        ]

        # All three verdicts appear above. The short form carries one row,
        # which is what a passing mention in a longer document needs.
        single = [rows[0]]
        return {"rows": rows, "single": single}

    def _validate_context(self, d):
        """`verdict` is one of three words the CSS colours.

        And all three should appear in the full table: a showcase where every
        row reads `rich` demonstrates one third of the component."""
        for key in ("rows", "single"):
            rows = d[key]
            assert_rows("valuation-multiples", key, rows,
                        ("multiple", "current", "peers", "history",
                         "premium", "verdict"))
            for i, r in enumerate(rows):
                assert_enum("valuation-multiples", f"{key}[{i}].verdict",
                            r["verdict"], {"cheap", "fair", "rich"})
        verdicts = {r["verdict"] for r in d["rows"]}
        assert verdicts == {"cheap", "fair", "rich"}, \
            (f"valuation-multiples: the full table shows {sorted(verdicts)}; "
             f"all three verdicts should appear, or the showcase demonstrates "
             f"only the tones it happens to use")

if __name__ == "__main__":
    print(ValuationMultiplesShowcaseController().build())
