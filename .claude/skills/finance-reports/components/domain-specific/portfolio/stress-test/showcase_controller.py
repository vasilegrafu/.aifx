"""Showcase controller for the `stress-test` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {scenario:str, trigger:str, impact:str, magnitude:num, tone:bad|warn, response:str} -- magnitude % drives the bar

ONE `tone` FEEDS TWO CLASS FAMILIES WITH DIFFERENT VOCABULARIES. It
is emitted as both tone-{{ tone }} on the figure and
portfolio-stress-fill-{{ tone }} on the bar, but portfolio.css defines
tone-good, tone-bad and tone-neutral for the first, and only
portfolio-stress-fill-bad and portfolio-stress-fill-warn for the second.

The intersection is ONE VALUE: "bad". Anything else styles one half and not
the other -- "warn" colours the bar and leaves the figure plain, "good"
colours the figure and leaves the bar plain. Both are used below so the split
is visible rather than described.

`magnitude` is the bar and `impact` is the text, and nothing ties them
together.
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


class StressTestShowcaseController(ShowcaseController):

    def _build_context(self):
        # magnitude is derived from the impact string, so the bar cannot
        # disagree with the number printed beside it.
        scenarios = [
            ("Rates +200bp", "Parallel shift across the curve", -12.4, "bad",
             "Duration cut to 3.1 years; add 4% to floating-rate credit"),
            ("Equity -20%", "Broad drawdown, correlations to 0.9", -18.6,
             "bad", "Hedge overlay covers the first 8%; no forced selling"),
            ("Credit spreads +150bp", "High yield reprices, IG follows",
             -7.2, "warn", "Rotate 3% from BB into short-dated IG"),
            ("USD +10%", "Flight to quality", -4.1, "warn",
             "Unhedged sleeve is 22% of assets; hedge ratio raised to 60%"),
        ]
        rows = [{"scenario": name, "trigger": trigger,
                 "impact": f"{impact:+.1f}%", "magnitude": abs(impact),
                 "tone": tone, "response": response}
                for name, trigger, impact, tone, response in scenarios]
        return {"rows": rows}

    def _validate_context(self, d):
        """The bar matches the number, and every tone is one the stylesheet
        has a rule for on at least one of the two elements it lands on."""
        assert_rows("stress-test", "rows", d["rows"],
                    ("scenario", "trigger", "impact", "magnitude", "tone",
                     "response"), 2)
        assert_all_drawn("stress-test", d, [("rows", ())])
        assert_labels("stress-test", "scenarios",
                      [r["scenario"] for r in d["rows"]])
        for r in d["rows"]:
            assert_numbers("stress-test", r["scenario"], [r["magnitude"]])
            assert 0 <= r["magnitude"] <= 100, \
                (f"stress-test: {r['scenario']!r} magnitude is "
                 f"{r['magnitude']}; outside 0..100 the fill leaves its track")
            assert abs(float(r["impact"].rstrip("%"))) == r["magnitude"], \
                (f"stress-test: {r['scenario']!r} prints {r['impact']} beside "
                 f"a bar drawn at {r['magnitude']}%")
            # Only "bad" has a rule in BOTH families; see the docstring.
            assert_enum("stress-test", f"{r['scenario']!r}.tone", r["tone"],
                        {"bad", "warn"})
            assert r["response"], \
                (f"stress-test: {r['scenario']!r} has no response; a stress "
                 f"test with no action attached is a worry, not a plan")

if __name__ == "__main__":
    print(StressTestShowcaseController().build())
