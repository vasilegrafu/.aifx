"""Showcase controller for the `drawdown-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {depth:str, peak:str, trough:str, recovery:str, decline_months:str, recovery_months:str, cause:str}

THE DEPTH COLUMN IS STYLED `neg` UNCONDITIONALLY, so a depth written
without its minus sign renders red and reads as a loss anyway -- the styling
will never tell you the sign is missing.

Three dates and two durations describe the same episode, and none of them is
checked against the others. Peak precedes trough precedes recovery, and the
two month counts are the gaps between them; the validator derives both from
the dates.
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


class DrawdownTableShowcaseController(ShowcaseController):

    def _build_context(self):
        from datetime import date

        # Dates first; the durations are computed from them.
        episodes = [
            (-31.4, date(2020, 2, 19), date(2020, 3, 23), date(2020, 8, 18),
             "Pandemic drawdown; fastest 30% decline on record"),
            (-24.8, date(2022, 1, 3), date(2022, 10, 12), date(2024, 1, 19),
             "Rate shock; the slowest recovery in the series"),
            (-16.2, date(2018, 9, 20), date(2018, 12, 24), date(2019, 4, 23),
             "Tightening cycle and trade tariffs"),
            (-9.7, date(2023, 7, 31), date(2023, 10, 27), date(2023, 12, 8),
             "Long-end yields above 5%"),
        ]

        def months(start, end):
            return round((end - start).days / 30.44, 1)

        rows = [{"depth": f"{depth:.1f}%",
                 "peak": peak.isoformat(),
                 "trough": trough.isoformat(),
                 "recovery": recovery.isoformat(),
                 "decline_months": f"{months(peak, trough)} mo",
                 "recovery_months": f"{months(trough, recovery)} mo",
                 "cause": cause}
                for depth, peak, trough, recovery, cause in episodes]
        return {"rows": rows}

    def _validate_context(self, d):
        """Dates run peak -> trough -> recovery, the durations are the gaps
        between them, and the episodes are ordered deepest first."""
        from datetime import date

        assert_rows("drawdown-table", "rows", d["rows"],
                    ("depth", "peak", "trough", "recovery", "decline_months",
                     "recovery_months", "cause"), 2)
        assert_all_drawn("drawdown-table", d, [("rows", ())])
        assert_labels("drawdown-table", "causes",
                      [r["cause"] for r in d["rows"]])

        depths = []
        for r in d["rows"]:
            depth = float(r["depth"].rstrip("%"))
            assert depth < 0, \
                (f"drawdown-table: depth {r['depth']!r} is not negative; the "
                 f"column is styled `neg` whatever the sign, so it would "
                 f"render red and read as a loss regardless")
            depths.append(depth)

            peak, trough, recovery = (date.fromisoformat(r[k]) for k in
                                      ("peak", "trough", "recovery"))
            assert peak < trough < recovery, \
                (f"drawdown-table: {r['cause'][:30]!r} runs {peak} -> "
                 f"{trough} -> {recovery}; a drawdown falls before it "
                 f"recovers")
            for start, end, key in ((peak, trough, "decline_months"),
                                    (trough, recovery, "recovery_months")):
                stated = float(r[key].rstrip(" mo"))
                actual = (end - start).days / 30.44
                assert abs(stated - actual) < 0.15, \
                    (f"drawdown-table: {r['cause'][:30]!r} {key} says "
                     f"{r[key]} but {start} to {end} is {actual:.1f} months")

        assert depths == sorted(depths), \
            (f"drawdown-table: depths {depths} are not deepest-first; the "
             f"row numbers imply a ranking the order does not follow")

if __name__ == "__main__":
    print(DrawdownTableShowcaseController().build())
