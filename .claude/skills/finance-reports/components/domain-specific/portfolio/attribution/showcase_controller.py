"""Showcase controller for the `attribution` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {segment:str, pw, bw, pr, br, allocation, selection, total -- all pre-formatted str}  total_row? {label, cells}

BRINSON ATTRIBUTION HAS ONE PROPERTY WORTH CHECKING and the macro
checks none of it: the effects must sum to the excess return they claim to
explain. Every cell here is a pre-formatted string, so a table that decomposes
1.40% of outperformance into effects totalling 0.83% renders exactly as
convincingly as a correct one.

The figures below are COMPUTED from the weights and returns:

    allocation = (Wp - Wb) x (Rb_segment - Rb_total)
    selection  = Wp x (Rp_segment - Rb_segment)

and the validator proves the totals reconcile to the +1.40% excess that the
performance-table showcase reports for the same strategy.
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


class AttributionShowcaseController(ShowcaseController):

    def _build_context(self):
        # weight and return, portfolio and benchmark, per segment.
        segments = [
            ("Technology", 32.0, 26.0, 18.4, 15.2),
            ("Financials", 21.0, 24.0, 7.1, 8.6),
            ("Healthcare", 27.0, 28.0, 12.9, 11.4),
            ("Industrials", 20.0, 22.0, 6.2, 6.8),
        ]
        rb_total = sum(bw / 100 * br for _, _, bw, _, br in segments)
        rp_total = sum(pw / 100 * pr for _, pw, _, pr, _ in segments)

        rows = []
        for name, pw, bw, pr, br in segments:
            allocation = (pw - bw) / 100 * (br - rb_total)
            selection = pw / 100 * (pr - br)
            rows.append({
                "segment": name,
                "pw": f"{pw:.1f}%", "bw": f"{bw:.1f}%",
                "pr": f"{pr:+.1f}%", "br": f"{br:+.1f}%",
                "allocation": f"{allocation:+.2f}%",
                "selection": f"{selection:+.2f}%",
                "total": f"{allocation + selection:+.2f}%",
            })

        allocation_total = sum((pw - bw) / 100 * (br - rb_total)
                               for _, pw, bw, _, br in segments)
        selection_total = sum(pw / 100 * (pr - br)
                              for _, pw, _, pr, br in segments)
        total_row = {"label": "Total",
                     "cells": ["100.0%", "100.0%",
                               f"{rp_total:+.1f}%", f"{rb_total:+.1f}%",
                               f"{allocation_total:+.2f}%",
                               f"{selection_total:+.2f}%",
                               f"{allocation_total + selection_total:+.2f}%"]}
        return {"rows": rows, "total_row": total_row,
                "excess": round(rp_total - rb_total, 2)}

    def _validate_context(self, d):
        """Weights sum to 100 on both sides, each row's total is its own two
        effects, and the effects reconcile to the excess return.

        The last one is the whole point of an attribution table: effects that
        do not sum to the outperformance are not explaining it."""
        assert_rows("attribution", "rows", d["rows"],
                    ("segment", "pw", "bw", "pr", "br", "allocation",
                     "selection", "total"), 2)
        assert_all_drawn("attribution", d, [("rows", ("total_row", "excess"))])
        assert_labels("attribution", "segments",
                      [r["segment"] for r in d["rows"]])

        def pct(text):
            return float(text.rstrip("%"))

        for side in ("pw", "bw"):
            weights = sum(pct(r[side]) for r in d["rows"])
            assert abs(weights - 100) < 0.05, \
                (f"attribution: {side} sums to {weights:.1f}%, not 100%; the "
                 f"effects below are computed against a portfolio that does "
                 f"not exist")

        allocation_total = selection_total = 0.0
        for r in d["rows"]:
            allocation, selection = pct(r["allocation"]), pct(r["selection"])
            allocation_total += allocation
            selection_total += selection
            # Three independently rounded strings, so the tolerance allows
            # half a display unit for each rather than assuming the printed
            # values add exactly.
            assert abs(allocation + selection - pct(r["total"])) <= 0.0151, \
                (f"attribution: {r['segment']!r} shows {r['allocation']} + "
                 f"{r['selection']} with a total of {r['total']}")

        assert abs(allocation_total + selection_total - d["excess"]) <= 0.05, \
            (f"attribution: effects sum to "
             f"{allocation_total + selection_total:+.2f}% against an excess "
             f"return of {d['excess']:+.2f}%; the table is decomposing "
             f"something other than the outperformance it reports")

        cells = d["total_row"]["cells"]
        assert len(cells) == 7, \
            f"attribution: total_row has {len(cells)} cells against 7 columns"
        assert abs(pct(cells[-1]) - d["excess"]) <= 0.02, \
            (f"attribution: the total row prints {cells[-1]} against an "
             f"excess return of {d['excess']:+.2f}%")

if __name__ == "__main__":
    print(AttributionShowcaseController().build())
