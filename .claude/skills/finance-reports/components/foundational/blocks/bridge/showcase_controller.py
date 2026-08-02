"""Showcase controller for the `bridge` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    steps[] {label:str, delta:num, kind:start|up|down|subtotal|end, display?:str}

SET scale_min AND scale_max. They default to 0..100, and these steps
run to 38,549 -- every bar would compute an offset far past 100% and leave its
track, exactly as valuation-range did.

THE STEPS MUST CARRY START TO END. `delta` is the VALUE for start, end and
subtotal, and the CHANGE for up and down; a bridge whose movements do not
land on its own endpoint still draws, and looks convincing. The validator
below replays the macro's own walk and refuses that.
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


class BridgeShowcaseController(ShowcaseController):

    def _build_context(self):
        # FY24 -> FY25 revenue. 34,200 + 5,100 + 1,340 - 1,180 - 911 = 38,549,
        # which is the revenue every other showcase in this library uses.
        revenue = [
            {"label": "FY24 revenue", "delta": 34200, "kind": "start"},
            {"label": "New logos", "delta": 5100, "kind": "up"},
            {"label": "Expansion", "delta": 1340, "kind": "up"},
            {"label": "Churn", "delta": -1180, "kind": "down"},
            {"label": "FX translation", "delta": -911, "kind": "down"},
            {"label": "FY25 revenue", "delta": 38549, "kind": "end"},
        ]

        # The same shape with a subtotal, which RESETS the running total rather
        # than adding to it: 17,600 + 1,940 + 820 = 20,360, then the cost lines
        # take it to 19,081.
        gross = [
            {"label": "FY24 gross profit", "delta": 17600, "kind": "start"},
            {"label": "Volume", "delta": 1940, "kind": "up"},
            {"label": "Price and mix", "delta": 820, "kind": "up"},
            {"label": "Before input cost", "delta": 20360, "kind": "subtotal"},
            {"label": "Input cost", "delta": -980, "kind": "down"},
            {"label": "FX translation", "delta": -299, "kind": "down"},
            {"label": "FY25 gross profit", "delta": 19081, "kind": "end"},
        ]
        return {"revenue": revenue, "gross": gross,
                "revenue_max": 42000, "gross_max": 22000}

    @staticmethod
    def _walk(steps):
        """Replay the macro's cumulative logic and return (lo, hi) per step.

        Copied in behaviour from component.html.j2 rather than imported,
        because the macro computes it inline -- if that logic changes, this
        stops agreeing and the showcase says so."""
        cum, spans = 0, []
        for s in steps:
            if s["kind"] in ("start", "end", "subtotal"):
                lo, hi, cum = 0, s["delta"], s["delta"]
            elif s["delta"] >= 0:
                lo, hi, cum = cum, cum + s["delta"], cum + s["delta"]
            else:
                lo, hi, cum = cum + s["delta"], cum, cum + s["delta"]
            spans.append((lo, hi))
        return spans

    def _validate_context(self, d):
        """The movements reach the endpoint, and every bar fits its track."""
        assert_all_drawn("bridge", d, [("revenue", ("revenue_max",)),
                                       ("gross", ("gross_max",))])
        kinds = {"start", "up", "down", "subtotal", "end"}
        for key, cap in (("revenue", "revenue_max"), ("gross", "gross_max")):
            steps = d[key]
            assert_rows("bridge", key, steps, ("label", "delta", "kind"), 3)
            assert_numbers("bridge", key, [s["delta"] for s in steps])
            for s in steps:
                assert_enum("bridge", f"{key}[{s['label']!r}].kind",
                            s["kind"], kinds)
            assert steps[0]["kind"] == "start" and steps[-1]["kind"] == "end", \
                f"bridge: {key} must open on a start step and close on an end"

            # The assertion the header asks for: the walk must land on the
            # endpoint the last step claims.
            spans = self._walk(steps)
            reached = spans[-2][1] if steps[-2]["delta"] >= 0 else spans[-2][0]
            claimed = steps[-1]["delta"]
            assert abs(reached - claimed) < 0.01, \
                (f"bridge: {key} movements reach {reached} but the end step "
                 f"claims {claimed}; the bridge would draw and look convincing")

            # And the same trap valuation-range fell into.
            span = d[cap]
            for (lo, hi), s in zip(spans, steps):
                assert 0 <= lo <= span and 0 <= hi <= span, \
                    (f"bridge: {key} step {s['label']!r} spans {lo}..{hi}, "
                     f"outside the 0..{span} scale; the bar leaves its track")

if __name__ == "__main__":
    print(BridgeShowcaseController().build())
