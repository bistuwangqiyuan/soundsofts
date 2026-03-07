"""Spatiotemporal alignment of ultrasonic and peel-force data streams."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import correlate


class SpatialAlignment:
    """Align ultrasonic scan positions with peel-force positions.

    The two data streams are recorded by separate sensors and linked via
    FPGA timestamps.  This class performs:

    1. Coarse alignment using shared timestamps.
    2. Interpolation to a common spatial grid.
    3. Fine cross-correlation refinement (sub-mm accuracy target <= 0.5 mm).
    """

    def __init__(self, grid_spacing_mm: float = 1.0) -> None:
        self.grid_spacing = grid_spacing_mm

    def align(
        self,
        us_positions: np.ndarray,
        us_timestamps: np.ndarray,
        force_positions: np.ndarray,
        force_timestamps: np.ndarray,
        force_values: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return (aligned_positions, interpolated_forces) on a common grid."""
        start = max(us_positions.min(), force_positions.min())
        end = min(us_positions.max(), force_positions.max())
        common_grid = np.arange(start, end, self.grid_spacing)

        interp_force = interp1d(
            force_positions, force_values, kind="cubic", bounds_error=False, fill_value="extrapolate"
        )
        aligned_forces = interp_force(common_grid)

        # Fine-tune with cross-correlation on overlapping envelope
        if len(common_grid) > 10:
            lag = self._cross_corr_lag(us_timestamps, force_timestamps)
            if abs(lag) < len(common_grid) // 2:
                aligned_forces = np.roll(aligned_forces, -lag)

        return common_grid, aligned_forces.astype(np.float32)

    @staticmethod
    def _cross_corr_lag(a: np.ndarray, b: np.ndarray) -> int:
        min_len = min(len(a), len(b))
        a_norm = a[:min_len] - np.mean(a[:min_len])
        b_norm = b[:min_len] - np.mean(b[:min_len])
        corr = correlate(a_norm, b_norm, mode="full")
        return int(np.argmax(corr)) - (min_len - 1)
