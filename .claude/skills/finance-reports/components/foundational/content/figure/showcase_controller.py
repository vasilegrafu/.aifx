"""Showcase controller for the `figure` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    src: str   alt: str -- REQUIRED, never empty   caption: str

ALT IS NOT THE CAPTION. The caption is read by everyone and says what
the figure shows; the alt text is read INSTEAD of the figure and must carry
what the figure carries. Duplicating one into the other leaves a screen-reader
user with the label and none of the content, which is the failure that looks
like compliance.

The image below is an inline data URI so the page stays self-contained.
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


class FigureShowcaseController(ShowcaseController):

    def _build_context(self):
        # A data URI, so the showcase has no external dependency and cannot
        # render as a broken image if the network is unavailable.
        bars = "".join(
            f"<rect x='{20 + i * 46}' y='{140 - h}' width='30' height='{h}' "
            f"fill='rgb(31,78,121)'/>"
            for i, h in enumerate([62, 71, 80, 89, 100]))
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='260' "
               "height='160' viewBox='0 0 260 160'>"
               "<rect width='260' height='160' fill='rgb(245,247,250)'/>"
               f"{bars}"
               "<line x1='14' y1='140' x2='250' y2='140' "
               "stroke='rgb(160,170,185)' stroke-width='1'/></svg>")
        return {"src": "data:image/svg+xml;utf8," + svg,
                "alt": "Revenue rises in each of the five years, from 24.1 to "
                       "38.5 billion dollars, with the largest step in FY25.",
                "caption": "Revenue, FY21 to FY25 ($bn)"}

    def _validate_context(self, d):
        """Alt is present, is not a copy of the caption, and says something.

        The check that matters is the second one: an alt equal to the caption
        passes every automated accessibility test and still tells a
        screen-reader user nothing the sighted reader was not also told."""
        assert_all_drawn("figure", d, [("src", ("alt", "caption"))])
        assert d["alt"].strip(), \
            "figure: alt is required; an empty alt hides the figure entirely"
        assert d["alt"].strip().lower() != d["caption"].strip().lower(), \
            ("figure: alt duplicates the caption; the caption says what the "
             "figure IS and the alt has to say what it SHOWS")
        assert len(d["alt"].split()) >= 8, \
            (f"figure: alt is {len(d['alt'].split())} words; it stands in for "
             f"the whole figure, not for its title")
        assert d["src"].startswith("data:") or "/" in d["src"], \
            "figure: src is neither a data URI nor a path"

if __name__ == "__main__":
    print(FigureShowcaseController().build())
