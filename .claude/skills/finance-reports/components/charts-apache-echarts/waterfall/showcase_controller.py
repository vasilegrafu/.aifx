"""Showcase controller for the `waterfall` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    steps[] {label:str, value:num, kind:start|delta|total}

THE STEPS MUST RECONCILE: start plus every delta equals the total.
Nothing in the rendering checks it, so _validate_context does -- a waterfall
that does not tie is the same failure as a sankey that does not conserve.
"""

import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import assert_labels, assert_numbers    # noqa: E402
from components._showcase_controller import ShowcaseController     # noqa: E402


class ChartWaterfallShowcaseController(ShowcaseController):

    def _build_context(self):
        # A revenue bridge across four years. The deltas are real segment
        # movements and they tie to the closing figure -- proved below, not
        # assumed.
        revenue_bridge = [
            {"label": "FY21 revenue", "value": 16434, "kind": "start"},
            {"label": "Data Center", "value": 16635, "kind": "delta"},
            {"label": "Client and Gaming", "value": 14550, "kind": "delta"},
            {"label": "Gaming", "value": 3910, "kind": "delta"},
            {"label": "Embedded", "value": 3454, "kind": "delta"},
            {"label": "Graphics and Visual", "value": -7102, "kind": "delta"},
            {"label": "Computing and Graphics", "value": -9332, "kind": "delta"},
            {"label": "FY25 revenue", "value": 38549, "kind": "total"},
        ]

        # Margin walk: smaller, and every delta negative except one, so the
        # falling staircase is the shape.
        margin_walk = [
            {"label": "Gross profit", "value": 19081, "kind": "start"},
            {"label": "R&D", "value": -9019, "kind": "delta"},
            {"label": "SG&A", "value": -3210, "kind": "delta"},
            {"label": "Other operating", "value": -1104, "kind": "delta"},
            {"label": "Operating income", "value": 5748, "kind": "total"},
        ]

        return {"revenue_bridge": revenue_bridge, "margin_walk": margin_walk}

    def _validate_context(self, d):
        """RECONCILIATION -- the check only this component can make.

        usage.md: "start plus every delta must equal the end. Nothing in the
        rendering checks this, and a waterfall that does not tie is a chart
        that lies"."""
        for key in ("revenue_bridge", "margin_walk"):
            steps = d[key]
            assert_labels("waterfall", f"{key} labels", [s["label"] for s in steps])
            assert_numbers("waterfall", f"{key} values", [s["value"] for s in steps])

            kinds = [s["kind"] for s in steps]
            for k in kinds:
                assert k in ("start", "delta", "total"), \
                    f"waterfall: {key} has kind {k!r}; one of start, delta, total"
            assert kinds[0] == "start" and kinds[-1] == "total", \
                (f"waterfall: {key} runs {kinds[0]!r}..{kinds[-1]!r}; a bridge "
                 f"starts at a start and lands on a total")

            start = steps[0]["value"]
            deltas = sum(s["value"] for s in steps if s["kind"] == "delta")
            total = steps[-1]["value"]
            assert start + deltas == total, \
                (f"waterfall: {key} does not tie -- {start} + {deltas} = "
                 f"{start + deltas}, but the total says {total}. The chart "
                 f"would draw a staircase that lands nowhere in particular")

if __name__ == "__main__":
    print(ChartWaterfallShowcaseController().build())
