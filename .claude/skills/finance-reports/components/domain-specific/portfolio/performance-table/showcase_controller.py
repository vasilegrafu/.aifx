"""Showcase controller for the `performance-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {label:str, cells:str[], kind?:portfolio-benchmark|portfolio-excess} -- pre-formatted % strings

`kind` CARRIES THE PREFIX -- portfolio-benchmark, portfolio-excess. It is
emitted as the class verbatim and portfolio.css styles tr.portfolio-benchmark
and tr.portfolio-excess, so a bare "benchmark" renders unstyled and the
benchmark row reads as another portfolio line.

EVERY CELL IS A STRING and nothing checks the excess row against the two above
it. The validator does.
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


class PerformanceTableShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["1M", "3M", "YTD", "1Y", "3Y ann.", "5Y ann."]
        portfolio = [2.4, 5.1, 9.8, 14.2, 11.6, 10.3]
        benchmark = [1.9, 4.4, 8.1, 12.7, 10.9, 9.8]
        excess = [round(p - b, 1) for p, b in zip(portfolio, benchmark)]

        def cells(values):
            return [f"{v:+.1f}%" for v in values]

        # The prefix is part of the value: the macro emits `kind` as the
        # class verbatim, and portfolio.css styles tr.portfolio-benchmark
        # and tr.portfolio-excess.
        rows = [
            {"label": "Strategy", "cells": cells(portfolio)},
            {"label": "MSCI World", "cells": cells(benchmark),
             "kind": "portfolio-benchmark"},
            {"label": "Excess", "cells": cells(excess),
             "kind": "portfolio-excess"},
        ]
        return {"periods": periods, "rows": rows}

    def _validate_context(self, d):
        """Every row spans the periods, and the excess row is the difference
        between the two above it -- read back out of the rendered strings."""
        assert_labels("performance-table", "periods", d["periods"])
        assert_all_drawn("performance-table", d, [("periods", ("rows",))])
        assert_rows("performance-table", "rows", d["rows"], ("label", "cells"), 3)
        assert_labels("performance-table", "labels",
                      [r["label"] for r in d["rows"]])

        for r in d["rows"]:
            assert len(r["cells"]) == len(d["periods"]), \
                (f"performance-table: {r['label']!r} has {len(r['cells'])} "
                 f"cells against {len(d['periods'])} periods")
            if r.get("kind"):
                assert_enum("performance-table", f"{r['label']!r}.kind",
                            r["kind"],
                            {"portfolio-benchmark", "portfolio-excess"})

        def numbers(row):
            return [float(v.rstrip("%")) for v in row["cells"]]

        strategy, bench, excess = (numbers(r) for r in d["rows"][:3])
        for i, period in enumerate(d["periods"]):
            assert abs(strategy[i] - bench[i] - excess[i]) < 0.05, \
                (f"performance-table: {period} shows {strategy[i]:+.1f}% "
                 f"against {bench[i]:+.1f}% with an excess of "
                 f"{excess[i]:+.1f}%, which does not subtract")

if __name__ == "__main__":
    print(PerformanceTableShowcaseController().build())
