"""Showcase controller for the `risk-metrics` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {metric:str, value:str, benchmark:str, note:str}

`subject_label` EXISTS BECAUSE IT WAS HARDCODED ONCE, as the component
header records: the subject column said "Strategy" while the benchmark column
was already configurable, and the first single-stock thesis to use this
component got a column headed Strategy describing one share. Both labels are
arguments now, and both are set below.

The `note` column is the reading, not a repeat of the number. A note saying
"Sharpe of 0.82" wastes the only column on the table that can say what the
figure means.
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


class RiskMetricsShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"metric": "Annualised return", "value": "10.3%",
             "benchmark": "9.8%", "note": "Ahead by 0.5pt over five years"},
            {"metric": "Annualised volatility", "value": "14.2%",
             "benchmark": "13.1%",
             "note": "1.1pt more variable than the index"},
            {"metric": "Sharpe ratio", "value": "0.58",
             "benchmark": "0.59",
             "note": "The extra return does not cover the extra risk"},
            {"metric": "Maximum drawdown", "value": "-31.4%",
             "benchmark": "-27.8%",
             "note": "Deeper trough, in the same month as the index"},
            {"metric": "Beta", "value": "1.06", "benchmark": "1.00",
             "note": "Slightly more exposed than the market"},
            {"metric": "Tracking error", "value": "4.8%", "benchmark": "--",
             "note": "Active enough for the fee to be a real question"},
            {"metric": "Information ratio", "value": "0.10",
             "benchmark": "--",
             "note": "0.5pt of excess for 4.8pt of tracking error"},
        ]
        return {"rows": rows, "subject": "Strategy",
                "benchmark": "MSCI World"}

    def _validate_context(self, d):
        """Metrics are distinct, both column labels are set, and no note
        merely restates the value beside it."""
        assert_rows("risk-metrics", "rows", d["rows"],
                    ("metric", "value", "benchmark", "note"), 3)
        assert_all_drawn("risk-metrics", d,
                         [("rows", ("subject", "benchmark"))])
        assert_labels("risk-metrics", "metrics",
                      [r["metric"] for r in d["rows"]])
        assert d["subject"] and d["benchmark"], \
            ("risk-metrics: both column labels must be set; subject_label was "
             "hardcoded once and headed a single-stock table 'Strategy'")
        for r in d["rows"]:
            assert r["note"], \
                f"risk-metrics: {r['metric']!r} has no reading"
            assert r["value"] not in r["note"], \
                (f"risk-metrics: {r['metric']!r} note repeats the value "
                 f"{r['value']!r}; the reading column is the only place the "
                 f"table can say what the number means")

if __name__ == "__main__":
    print(RiskMetricsShowcaseController().build())
