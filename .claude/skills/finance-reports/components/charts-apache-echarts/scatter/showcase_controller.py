"""Showcase controller for the `scatter` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points: [x,y] or [x,y,label]}

Points stay POSITIONAL -- [x, y] is what ECharts reads natively, and
a third element becomes the point's label. Both forms appear here, because the
macro branches on the length of the point.
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


class ChartScatterShowcaseController(ShowcaseController):

    def _build_context(self):
        # Two measures per company. The third element is the ticker, which
        # the macro renders as a point label -- the branch worth showing.
        semis = {"name": "Semiconductors", "points": [
            [23.4, 5.4, "AMD"], [8.6, 62.9, "NVDA"], [26.1, -0.1, "INTC"],
            [19.8, 28.4, "QCOM"], [12.2, 31.1, "AVGO"], [15.4, 18.9, "TXN"]]}
        software = {"name": "Software", "points": [
            [17.1, 34.2, "MSFT"], [21.9, 12.6, "CRM"], [14.4, 41.8, "ORCL"],
            [26.8, 8.1, "NOW"]]}

        # No labels: the same component when the CLOUD is the finding and
        # naming every point would be noise.
        unlabelled = {"name": "Russell 1000", "points": [
            [4.2, 11.1], [6.8, 14.3], [9.1, 8.7], [11.4, 19.2], [13.9, 16.8],
            [15.2, 24.1], [17.8, 21.5], [19.4, 29.7], [22.1, 26.3],
            [24.6, 33.8], [27.2, 30.1], [29.8, 38.4], [7.3, 6.2],
            [12.6, 12.9], [18.1, 17.4], [23.7, 22.8]]}

        # Y IN ABSOLUTE DOLLARS rather than a ratio. Points here are
        # POSITIONAL [x, y], so the y magnitudes have to be pulled out of the
        # pairs before the axis gap can be derived from them -- the one call
        # site where the shape of the data is not a plain list of numbers.
        by_size = {"name": "Semiconductors", "points": [
            [23.4, 22680, "AMD"], [8.6, 60922, "NVDA"], [26.1, 54228, "INTC"],
            [19.8, 35820, "QCOM"], [12.2, 35819, "AVGO"], [15.4, 17519, "TXN"]]}

        return {"semis": semis, "software": software,
                "unlabelled": unlabelled, "by_size": by_size}

    def _validate_context(self, d):
        """Points are POSITIONAL, so the checks are about length and order."""
        for key in ("semis", "software", "unlabelled", "by_size"):
            s = d[key]
            assert isinstance(s.get("name"), str) and s["name"], \
                f"scatter: {key!r} needs a non-empty name; it labels the legend"
            points = s["points"]
            assert points, f"scatter: {key!r} has no points"
            for i, p in enumerate(points):
                assert isinstance(p, list) and len(p) in (2, 3), \
                    (f"scatter: {key!r} point {i} has {len(p)} elements; a point "
                     f"is [x, y] or [x, y, label] and ECharts reads it by "
                     f"POSITION, so a third number would be drawn as a label")
                assert_numbers("scatter", f"{key!r} point {i}", p[:2])
                if len(p) == 3:
                    assert isinstance(p[2], str) and p[2], \
                        (f"scatter: {key!r} point {i} has a third element "
                         f"{p[2]!r}; the third slot is the label and must be a "
                         f"non-empty string")

if __name__ == "__main__":
    print(ChartScatterShowcaseController().build())
