"""Showcase controller for the `acceptance-criteria` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    id: str   title: str   given: str[]   when: str[]   then: str[]

GIVEN IS STATE, WHEN IS THE ACT, THEN IS THE OBSERVABLE RESULT. The
common failure is a `then` that restates the `when` -- "the report is
regenerated" is not an outcome anybody can check, and a criterion nobody can
check is a wish.
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


class AcceptanceCriteriaShowcaseController(ShowcaseController):

    def _build_context(self):
        regenerate = {
            "id": "AC-14",
            "title": "A new filing regenerates the report",
            "given": ["a published report built against the FY25 Q2 10-Q",
                      "a newer 10-Q available from the provider"],
            "when": ["the report controller runs against the same ticker"],
            "then": ["the page is rebuilt from the newer filing",
                     "every figure on the page carries the new period label",
                     "the asset version pin is unchanged"],
        }

        # A criterion whose `then` is about REFUSING to act. These get written
        # far less often than the happy path and are where the money is.
        refuse = {
            "id": "AC-15",
            "title": "A partial filing is refused, not rendered",
            "given": ["a 10-Q missing the cash flow statement"],
            "when": ["the report controller runs"],
            "then": ["the build stops with the missing statement named",
                     "no page is written",
                     "the previously published page is left in place"],
        }
        return {"regenerate": regenerate, "refuse": refuse}

    def _validate_context(self, d):
        """Each of given/when/then is a non-empty list of distinct strings.

        Distinct because a repeated clause is invisible in the rendered list
        and reads as emphasis rather than as the duplication it is."""
        assert_all_drawn("acceptance-criteria", d,
                         [("regenerate", ()), ("refuse", ())])
        for key, ac in d.items():
            for part in ("given", "when", "then"):
                assert_labels("acceptance-criteria", f"{key}.{part}", ac[part])
            assert ac["id"] and ac["title"], \
                f"acceptance-criteria: {key} needs an id and a title"
            assert len(ac["when"]) == 1, \
                (f"acceptance-criteria: {key} has {len(ac['when'])} `when` "
                 f"clauses; two acts in one criterion means a failure cannot "
                 f"be attributed to either")

if __name__ == "__main__":
    print(AcceptanceCriteriaShowcaseController().build())
