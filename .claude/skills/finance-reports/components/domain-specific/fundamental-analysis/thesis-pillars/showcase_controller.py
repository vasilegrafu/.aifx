"""Showcase controller for the `thesis-pillars` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {claim:str, evidence?:str, falsifier?:str}

THE FALSIFIER IS THE POINT. A claim with evidence is an argument; a
claim with evidence AND a stated way it could be wrong is a testable one, and
that is the difference between research and advocacy.
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


class ThesisPillarsShowcaseController(ShowcaseController):

    def _build_context(self):
        items = [
            {"claim": "Data centre demand is structural, not a build-out spike",
             "evidence": "Eight consecutive quarters of growth, and the "
                         "backlog extends 14 months",
             "falsifier": "Two consecutive quarters of flat or falling data "
                          "centre revenue with backlog under 6 months"},
            {"claim": "Foundry allocation is secured through the next node",
             "evidence": "Prepayments of $1.4bn disclosed in the Q1 filing",
             "falsifier": "Any quarter where units shipped fall short of "
                          "guidance and the shortfall is attributed to supply"},
            {"claim": "R&D at 23% of revenue is an investment, not a treadmill",
             "evidence": "Gross margin has risen 4 points across the same "
                         "period the R&D ratio rose",
             "falsifier": "Gross margin flat or falling for a year while R&D "
                          "stays above 22% of revenue"},
        ]

        # A claim with no falsifier stated -- included deliberately, because
        # the component must show what that looks like next to the others.
        partial = [
            {"claim": "The Embedded segment is stabilising",
             "evidence": "Down 2.9% against down 11% a year earlier"},
        ]
        return {"items": items, "partial": partial}

    def _validate_context(self, d):
        """A claim is required; evidence and falsifier are not, and the
        showcase shows both cases.

        Every pillar carrying a falsifier would hide what a bare claim looks
        like, which is the state a reader most needs to recognise."""
        for key in ("items", "partial"):
            assert_rows("thesis-pillars", key, d[key], ("claim",))
            for i, it in enumerate(d[key]):
                assert len(it["claim"].split()) >= 4, \
                    f"thesis-pillars: {key}[{i}] claim is too short to be one"
        assert all("falsifier" in i for i in d["items"]), \
            "thesis-pillars: the main set is the one that shows falsifiers"
        assert not any("falsifier" in i for i in d["partial"]), \
            ("thesis-pillars: the second set exists to show a claim WITHOUT a "
             "falsifier; giving it one leaves that state undemonstrated")

if __name__ == "__main__":
    print(ThesisPillarsShowcaseController().build())
