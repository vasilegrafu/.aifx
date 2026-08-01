"""Showcase controller for the `correlation-matrix` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    labels: str[]   matrix: num[][] -- matrix[i][j] is labels[i] vs labels[j]

THE SEQUENTIAL RAMP, not the categorical palette -- a correlation is
a magnitude, and colouring it categorically would say these are different
kinds rather than different amounts. The matrix must be square, symmetric and
carry 1.0 on its diagonal: a correlation with itself is the one value that
cannot be anything else.
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


class ChartCorrelationMatrixShowcaseController(ShowcaseController):

    def _build_context(self):
        labels = ["AMD", "NVDA", "INTC", "QCOM", "AVGO", "TXN"]

        # Symmetric with a unit diagonal -- proved in _validate_context, not
        # assumed. Written as the full square rather than a triangle, because
        # the macro reads matrix[i][j] directly.
        matrix = [
            [1.00, 0.82, 0.61, 0.58, 0.71, 0.49],
            [0.82, 1.00, 0.54, 0.62, 0.78, 0.51],
            [0.61, 0.54, 1.00, 0.47, 0.55, 0.63],
            [0.58, 0.62, 0.47, 1.00, 0.66, 0.57],
            [0.71, 0.78, 0.55, 0.66, 1.00, 0.60],
            [0.49, 0.51, 0.63, 0.57, 0.60, 1.00],
        ]

        # A set that actually goes negative, so the ramp shows both ends
        # rather than one half of itself.
        macro_labels = ["Equities", "Treasuries", "Gold", "Oil", "Dollar"]
        macro_matrix = [
            [1.00, -0.42, 0.11, 0.38, -0.29],
            [-0.42, 1.00, 0.34, -0.21, 0.18],
            [0.11, 0.34, 1.00, 0.09, -0.55],
            [0.38, -0.21, 0.09, 1.00, -0.16],
            [-0.29, 0.18, -0.55, -0.16, 1.00],
        ]

        return {"labels": labels, "matrix": matrix,
                "macro_labels": macro_labels, "macro_matrix": macro_matrix}

    def _validate_context(self, d):
        """SQUARE, SYMMETRIC, UNIT DIAGONAL.

        An asymmetric matrix draws two different colours for one relationship
        and the reader cannot tell which half is meant."""
        for lk, mk in (("labels", "matrix"), ("macro_labels", "macro_matrix")):
            labels, matrix = d[lk], d[mk]
            assert_labels("correlation-matrix", lk, labels)
            n = len(labels)
            assert len(matrix) == n, \
                (f"correlation-matrix: {mk} has {len(matrix)} rows against "
                 f"{n} {lk}; the heatmap indexes by position")
            for i, row in enumerate(matrix):
                assert len(row) == n, \
                    (f"correlation-matrix: {mk} row {i} has {len(row)} cells "
                     f"against {n} {lk}")
                assert_numbers("correlation-matrix", f"{mk} row {i}", row)
                assert row[i] == 1.0, \
                    (f"correlation-matrix: {mk}[{i}][{i}] is {row[i]}; "
                     f"{labels[i]!r} against itself is 1.0 and nothing else")
                for j in range(n):
                    assert -1.0 <= row[j] <= 1.0, \
                        (f"correlation-matrix: {mk}[{i}][{j}] is {row[j]}, "
                         f"outside -1..1; it is not a correlation")
                    assert row[j] == matrix[j][i], \
                        (f"correlation-matrix: {mk}[{i}][{j}]={row[j]} but "
                         f"[{j}][{i}]={matrix[j][i]}; one relationship would "
                         f"draw as two different colours")

if __name__ == "__main__":
    print(ChartCorrelationMatrixShowcaseController().build())
