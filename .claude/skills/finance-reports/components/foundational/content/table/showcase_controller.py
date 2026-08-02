"""Showcase controller for the `table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    headers: str[]   rows: any[][] -- each row as long as headers

`headers` AND `rows` ARE POSITIONAL AND REQUIRED -- the signature is
table(headers, rows, wide=false) with no defaults, so this is one of the few
macros that raises rather than rendering empty when it is called wrong.

The rows are a positional matrix with no keys, so a short row shifts every
cell after it under the wrong heading. `wide=true` lets a table scroll
sideways instead of squeezing; it is for column count, not for content.
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


class TableShowcaseController(ShowcaseController):

    def _build_context(self):
        headers = ["Filing", "Form", "Period", "Filed", "Pages"]
        rows = [
            ["FY25 Q2", "10-Q", "2026-06-30", "2026-07-24", 48],
            ["FY25 Q1", "10-Q", "2026-03-31", "2026-04-25", 46],
            ["FY24", "10-K", "2025-12-31", "2026-02-14", 212],
            ["FY24 Q3", "10-Q", "2025-09-30", "2025-10-23", 44],
        ]

        # The case wide=true is for: more columns than the page can hold.
        wide_headers = ["Segment", "FY21", "FY22", "FY23", "FY24", "FY25",
                        "CAGR", "FY25 margin", "Share of group"]
        # The segments add to the group revenue used everywhere else in this
        # library, in every year, and the margins weight to the group's 49.5%.
        wide_rows = [
            ["Platform", "9,640", "11,510", "13,600", "15,700", "18,120",
             "17.1%", "50.0%", "47.0%"],
            ["Services", "8,200", "8,940", "9,610", "10,320", "11,209",
             "8.1%", "38.9%", "29.1%"],
            ["Licensing", "6,260", "6,950", "7,690", "8,180", "9,220",
             "10.2%", "61.4%", "23.9%"],
        ]
        return {"headers": headers, "rows": rows,
                "wide_headers": wide_headers, "wide_rows": wide_rows,
                "group": [24100, 27400, 30900, 34200, 38549],
                "group_margin": 49.5}

    def _validate_context(self, d):
        """Every row matches its headers in width.

        The only check available: the matrix carries no keys, so nothing else
        about it can be verified from here."""
        assert_all_drawn("table", d,
                         [("headers", ("rows",)),
                          ("wide_headers", ("wide_rows", "group",
                                            "group_margin"))])
        for head_key, row_key in (("headers", "rows"),
                                  ("wide_headers", "wide_rows")):
            headers = d[head_key]
            assert_labels("table", head_key, headers)
            assert isinstance(d[row_key], list) and d[row_key], \
                f"table: {row_key} is empty"
            for i, row in enumerate(d[row_key]):
                assert len(row) == len(headers), \
                    (f"table: {row_key}[{i}] has {len(row)} cells against "
                     f"{len(headers)} headers; the row renders short and "
                     f"every cell after the gap sits under the wrong heading")

        # A positional matrix cannot check its own keys, but it CAN be checked
        # against the group it decomposes -- which is the only claim in the
        # table a reader would actually rely on.
        def money(text):
            return float(text.replace(",", ""))

        for year in range(len(d["group"])):
            total = sum(money(r[1 + year]) for r in d["wide_rows"])
            assert total == d["group"][year], \
                (f"table: segments sum to {total:,.0f} in "
                 f"{d['wide_headers'][1 + year]} against group revenue of "
                 f"{d['group'][year]:,}; the split does not decompose the "
                 f"total it claims to")

        shares = [float(r[-1].rstrip("%")) for r in d["wide_rows"]]
        assert abs(sum(shares) - 100) < 0.15, \
            f"table: segment shares sum to {sum(shares):.1f}%, not 100%"
        for r, share in zip(d["wide_rows"], shares):
            actual = 100 * money(r[5]) / d["group"][-1]
            assert abs(actual - share) < 0.1, \
                (f"table: {r[0]!r} is {actual:.1f}% of group revenue but "
                 f"prints {r[-1]}")

        # The margins have to weight back to the group's, or the segment
        # split is describing a different company from the income statement.
        weighted = sum(share / 100 * float(r[7].rstrip("%"))
                       for r, share in zip(d["wide_rows"], shares))
        assert abs(weighted - d["group_margin"]) < 0.1, \
            (f"table: segment margins weight to {weighted:.2f}% against a "
             f"group gross margin of {d['group_margin']}%")

if __name__ == "__main__":
    print(TableShowcaseController().build())
