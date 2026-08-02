"""Showcase controller for the `formula` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

It accepts EITHER form: formula(tex="...") or a {% call %} block.

KaTeX RENDERS THIS IN THE BROWSER, at view time, so a malformed
expression is not a build failure -- it is the raw TeX sitting on the page, or
nothing at all. Nothing in the build can tell you the maths is wrong.

BACKSLASHES ARE THE HAZARD. In a Python string \f and \t are escape
sequences, so `"\frac"` is a form feed followed by "rac" and the formula
silently loses its command. Every expression here is a RAW string.
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


class FormulaShowcaseController(ShowcaseController):

    def _build_context(self):
        # RAW strings. Without the r prefix, \f and \t are escape sequences
        # and the command is destroyed before Jinja or KaTeX ever sees it.
        return {
            "wacc": r"\text{WACC} = \frac{E}{V} \cdot R_e + "
                    r"\frac{D}{V} \cdot R_d \cdot (1 - T_c)",
            "gordon": r"V_0 = \frac{FCF_1}{r - g}",
            "sharpe": r"S = \frac{R_p - R_f}{\sigma_p}",
        }

    def _validate_context(self, d):
        """Braces balance and no command has been eaten by an escape sequence.

        The second check is the one that matters: a control character where a
        backslash should be renders as missing maths in the browser and as
        nothing at all in the build."""
        assert_all_drawn("formula", d, [("wacc", ("gordon", "sharpe"))])
        for key, tex in d.items():
            assert tex.count("{") == tex.count("}"), \
                (f"formula: {key} has {tex.count('{')} open braces against "
                 f"{tex.count('}')} closed; KaTeX renders nothing at all")
            for bad in ("\f", "\t", "\n", "\r", "\v", "\b", "\a"):
                assert bad not in tex, \
                    (f"formula: {key} contains a control character where a "
                     f"TeX command should be -- the string is missing its r "
                     f"prefix, so a command like \\frac was consumed as an "
                     f"escape sequence")
            assert "\\" in tex, \
                f"formula: {key} contains no TeX command at all"

if __name__ == "__main__":
    print(FormulaShowcaseController().build())
