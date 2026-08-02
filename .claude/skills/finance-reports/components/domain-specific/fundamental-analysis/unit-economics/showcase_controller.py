"""Showcase controller for the `unit-economics` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    headline[] {label, value}   rows[] {metric:str, value:str, benchmark:str, reading:str}

EVERY ROW CARRIES ITS BENCHMARK. A unit economic without one is a
number nobody can judge -- "gross margin 52%" means nothing until you know the
peer set runs 40-60.
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


class UnitEconomicsShowcaseController(ShowcaseController):

    def _build_context(self):
        headline = [
            {"label": "Revenue per employee", "value": "$1.42m"},
            {"label": "Gross profit per employee", "value": "$702k"},
            {"label": "R&D per engineer", "value": "$318k"},
        ]

        rows = [
            {"metric": "Gross margin", "value": "49.5%", "benchmark": "40 – 60%",
             "reading": "Mid-range for a fabless designer"},
            {"metric": "R&D / revenue", "value": "23.4%", "benchmark": "12 – 26%",
             "reading": "Top of the range; the strategy is visible here"},
            {"metric": "Capex / revenue", "value": "2.8%", "benchmark": "2 – 30%",
             "reading": "Fabless, so near the floor. INTC is at 27.7%"},
            {"metric": "SBC / revenue", "value": "4.7%", "benchmark": "3 – 6%",
             "reading": "Ordinary for the sector, and real money"},
        ]
        return {"headline": headline, "rows": rows}

    def _validate_context(self, d):
        """Every row has a benchmark AND a reading -- a number and a sentence.

        The reading is what stops the table being four figures the reader has
        to interpret unaided."""
        assert_rows("unit-economics", "headline", d["headline"], ("label", "value"))
        assert_rows("unit-economics", "rows", d["rows"],
                    ("metric", "value", "benchmark", "reading"))
        for i, r in enumerate(d["rows"]):
            for field in ("value", "benchmark", "reading"):
                assert isinstance(r[field], str) and r[field].strip(), \
                    (f"unit-economics: rows[{i}] {r['metric']!r} has an empty "
                     f"{field}; a metric without its {field} is a number "
                     f"nobody can judge")

if __name__ == "__main__":
    print(UnitEconomicsShowcaseController().build())
