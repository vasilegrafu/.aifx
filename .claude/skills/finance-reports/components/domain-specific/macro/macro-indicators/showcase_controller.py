"""Showcase controller for the `macro-indicators` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {indicator:str, latest:str, prior:str, consensus:str, surprise:str, dir:up|down|flat}

SURPRISE IS AGAINST CONSENSUS; `dir` IS AGAINST PRIOR. They are two
different comparisons and both are free strings, so a reading that beat
expectations while falling from last month can be written up as though it rose
-- which is the commonest way this table misleads.

Every surprise below is computed as latest minus consensus, and every `dir`
from latest against prior.
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


class MacroIndicatorsShowcaseController(ShowcaseController):

    def _build_context(self):
        # (indicator, latest, prior, consensus, unit)
        readings = [
            ("CPI, year on year", 3.1, 3.4, 3.2, "%"),
            ("Core PCE, year on year", 2.7, 2.8, 2.6, "%"),
            ("Unemployment rate", 4.3, 4.1, 4.2, "%"),
            ("ISM manufacturing", 48.6, 47.9, 49.1, ""),
            ("Retail sales, month on month", 0.4, 0.1, 0.3, "%"),
            ("10-year yield", 4.12, 4.31, 4.20, "%"),
        ]
        rows = []
        for indicator, latest, prior, consensus, unit in readings:
            move = latest - prior
            rows.append({
                "indicator": indicator,
                "latest": f"{latest}{unit}",
                "prior": f"{prior}{unit}",
                "consensus": f"{consensus}{unit}",
                # Against CONSENSUS, not against prior.
                "surprise": f"{latest - consensus:+.1f}",
                # Against PRIOR, not against consensus.
                "dir": "flat" if abs(move) < 0.05 else (
                    "up" if move > 0 else "down"),
            })
        return {"rows": rows}

    def _validate_context(self, d):
        """The surprise is latest minus consensus and the arrow is latest
        against prior -- the two comparisons this table is easiest to conflate."""
        assert_rows("macro-indicators", "rows", d["rows"],
                    ("indicator", "latest", "prior", "consensus", "surprise",
                     "dir"), 2)
        assert_all_drawn("macro-indicators", d, [("rows", ())])
        assert_labels("macro-indicators", "indicators",
                      [r["indicator"] for r in d["rows"]])

        def number(text):
            return float(text.rstrip("%"))

        for r in d["rows"]:
            assert_enum("macro-indicators", f"{r['indicator']!r}.dir",
                        r["dir"], {"up", "down", "flat"})
            latest = number(r["latest"])
            prior = number(r["prior"])
            consensus = number(r["consensus"])

            assert abs(number(r["surprise"]) - (latest - consensus)) < 0.051, \
                (f"macro-indicators: {r['indicator']!r} prints a surprise of "
                 f"{r['surprise']} against a consensus of {r['consensus']}; "
                 f"latest less consensus is {latest - consensus:+.1f}")

            move = latest - prior
            expected = "flat" if abs(move) < 0.05 else (
                "up" if move > 0 else "down")
            assert r["dir"] == expected, \
                (f"macro-indicators: {r['indicator']!r} moved {prior} -> "
                 f"{latest} but the arrow says {r['dir']!r}; the arrow is "
                 f"against PRIOR, not against consensus")

if __name__ == "__main__":
    print(MacroIndicatorsShowcaseController().build())
