"""Showcase controller for the `approval-block` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {name:str, role:str}

A SIGN-OFF BLOCK NAMES PEOPLE, NOT DEPARTMENTS. "Finance" cannot
approve anything; a person in finance can. The component takes a role beside
each name so the reader can tell whether the right people signed.
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


class ApprovalBlockShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"name": "A. Okonkwo", "role": "Head of Equity Research"},
            {"name": "M. Halvorsen", "role": "Chief Investment Officer"},
            {"name": "R. Delacroix", "role": "Compliance"},
        ]
        # The smallest form worth drawing. One signatory still needs the role
        # printed, or the block says only that somebody agreed.
        single = [{"name": "A. Okonkwo", "role": "Head of Equity Research"}]
        return {"rows": rows, "single": single}

    def _validate_context(self, d):
        """Names are distinct; a table listing one person twice is a mistake
        that reads as thoroughness."""
        assert_all_drawn("approval-block", d, [("rows", ()), ("single", ())])
        for key in ("rows", "single"):
            assert_rows("approval-block", key, d[key], ("name", "role"))
            assert_labels("approval-block", f"{key} names",
                          [r["name"] for r in d[key]])

if __name__ == "__main__":
    print(ApprovalBlockShowcaseController().build())
