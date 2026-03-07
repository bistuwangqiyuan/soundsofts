"""Linear and cubic-spline interpolation utilities."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import interp1d


class SignalInterpolator:
    """Resample signals onto a uniform spatial grid."""

    def __init__(self, kind: str = "cubic") -> None:
        self.kind = kind

    def interpolate(
        self,
        positions: np.ndarray,
        values: np.ndarray,
        target_positions: np.ndarray,
    ) -> np.ndarray:
        fn = interp1d(positions, values, kind=self.kind, bounds_error=False, fill_value="extrapolate")
        return fn(target_positions).astype(values.dtype)
