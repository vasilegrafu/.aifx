"""Showcase controller for the `segment-reporting` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {segment:str, revenue:num, rev_share:num, growth:num, profit?:num, profit_share?:num, margin?:num}   total_row? {label, cells}

SHARES, MARGIN AND GROWTH ARE PERCENT NUMBERS -- 52.4, never 0.524.
The macro formats them as percentages, so a fraction renders as 0.5% and looks
like a very small share rather than a very wrong one.
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


class SegmentReportingShowcaseController(ShowcaseController):

    def _build_context(self):
        # Shares sum to 100 and each is derived from the revenue column --
        # checked below rather than typed twice and hoped for.
        revenue = [("Data Center", 16635, 32.2), ("Client and Gaming", 14550, 0.0),
                   ("Gaming", 3910, 50.7), ("Embedded", 3454, -2.9)]
        total = sum(r for _, r, _ in revenue)
        rows = [{"segment": n, "revenue": r,
                 "rev_share": round(100 * r / total, 1), "growth": g}
                for n, r, g in revenue]

        total_row = {"label": "Total",
                     "cells": [f"{total:,}", "100.0%", "49.5%"]}

        # The wider form: profitability by segment, where a segment can be a
        # large share of revenue and a small share of profit.
        with_profit = [
            {"segment": "Data Center", "revenue": 16635, "rev_share": 43.2,
             "growth": 32.2, "profit": 3510, "profit_share": 61.1, "margin": 21.1},
            {"segment": "Client and Gaming", "revenue": 14550, "rev_share": 37.7,
             "growth": 0.0, "profit": 1420, "profit_share": 24.7, "margin": 9.8},
            {"segment": "Gaming", "revenue": 3910, "rev_share": 10.1,
             "growth": 50.7, "profit": 490, "profit_share": 8.5, "margin": 12.5},
            {"segment": "Embedded", "revenue": 3454, "rev_share": 9.0,
             "growth": -2.9, "profit": 326, "profit_share": 5.7, "margin": 9.4},
        ]

        return {"rows": rows, "total_row": total_row, "with_profit": with_profit}

    def _validate_context(self, d):
        """Shares are PERCENT NUMBERS and they sum to 100.

        A fraction (0.432) renders as 0.4% -- a very small share rather than a
        very wrong one, which is why it is worth catching here."""
        for key in ("rows", "with_profit"):
            rows = d[key]
            assert_rows("segment-reporting", key, rows,
                        ("segment", "revenue", "rev_share", "growth"))
            for i, r in enumerate(rows):
                assert_numbers("segment-reporting", f"{key}[{i}]",
                               [r["revenue"], r["rev_share"], r["growth"]])
                assert 0 <= r["rev_share"] <= 100, \
                    (f"segment-reporting: {key}[{i}] {r['segment']!r} has "
                     f"rev_share {r['rev_share']}; these are PERCENT NUMBERS "
                     f"(52.4), not fractions (0.524)")
            total = sum(r["rev_share"] for r in rows)
            assert abs(total - 100) < 0.3, \
                (f"segment-reporting: {key} shares sum to {total:.1f}, not 100; "
                 f"the column would read as a decomposition of something else")

if __name__ == "__main__":
    print(SegmentReportingShowcaseController().build())
