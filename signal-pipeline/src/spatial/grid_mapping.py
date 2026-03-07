"""Map scan positions to pipe / plate grids."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class GridCell:
    row: int
    col: int
    label: str  # e.g. "R03C07"


class GridMapper:
    """Assign scan positions to a regular grid.

    For pipe specimens the default is 12 rows x 10 columns (circumferential x axial).
    For plate specimens a single-row longitudinal band layout is used.
    """

    def __init__(self, rows: int = 12, cols: int = 10) -> None:
        self.rows = rows
        self.cols = cols

    def map_positions(
        self,
        x: np.ndarray,
        y: np.ndarray,
    ) -> list[GridCell]:
        """Assign each (x, y) point to a grid cell."""
        x_min, x_max = float(x.min()), float(x.max())
        y_min, y_max = float(y.min()), float(y.max())

        x_span = (x_max - x_min) or 1.0
        y_span = (y_max - y_min) or 1.0

        cells: list[GridCell] = []
        for xi, yi in zip(x, y):
            c = min(int((xi - x_min) / x_span * self.cols), self.cols - 1)
            r = min(int((yi - y_min) / y_span * self.rows), self.rows - 1)
            cells.append(GridCell(row=r, col=c, label=f"R{r:02d}C{c:02d}"))
        return cells

    def region_id(self, row: int, col: int) -> str:
        return f"R{row:02d}C{col:02d}"
