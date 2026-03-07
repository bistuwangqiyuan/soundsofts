"""Tests for spatial alignment and grid mapping."""

import numpy as np

from src.spatial import SpatialAlignment, GridMapper, SignalInterpolator


class TestSpatialAlignment:
    def test_basic_alignment(self):
        positions = np.arange(0, 100, 1.0)
        timestamps = np.arange(len(positions), dtype=np.float64)
        forces = np.sin(positions / 10.0).astype(np.float32)

        aligner = SpatialAlignment(grid_spacing_mm=1.0)
        grid, aligned = aligner.align(positions, timestamps, positions, timestamps, forces)
        assert len(grid) == len(aligned)
        assert len(grid) > 0


class TestGridMapper:
    def test_maps_to_grid(self):
        mapper = GridMapper(rows=12, cols=10)
        x = np.array([0.0, 50.0, 99.0])
        y = np.array([0.0, 50.0, 99.0])
        cells = mapper.map_positions(x, y)
        assert len(cells) == 3
        assert cells[0].label.startswith("R")


class TestInterpolator:
    def test_linear_interp(self):
        interp = SignalInterpolator(kind="linear")
        pos = np.array([0.0, 1.0, 2.0, 3.0])
        vals = np.array([0.0, 1.0, 4.0, 9.0], dtype=np.float32)
        target = np.array([0.5, 1.5, 2.5])
        result = interp.interpolate(pos, vals, target)
        assert len(result) == 3
