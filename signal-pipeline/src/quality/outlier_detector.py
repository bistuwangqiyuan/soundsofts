"""Outlier detection using IQR and Z-score methods."""

from __future__ import annotations

import numpy as np


class OutlierDetector:
    """Detect and optionally replace outlier samples."""

    def __init__(self, method: str = "iqr", threshold: float = 1.5) -> None:
        self.method = method
        self.threshold = threshold

    def detect(self, values: np.ndarray) -> np.ndarray:
        """Return boolean mask where ``True`` marks an outlier."""
        if self.method == "zscore":
            z = np.abs((values - np.mean(values)) / (np.std(values) + 1e-12))
            return z > self.threshold

        # IQR method
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        lower = q1 - self.threshold * iqr
        upper = q3 + self.threshold * iqr
        return (values < lower) | (values > upper)

    def clip(self, values: np.ndarray) -> np.ndarray:
        """Replace outliers with boundary values."""
        mask = self.detect(values)
        result = values.copy()
        if not np.any(mask):
            return result
        valid = values[~mask]
        if len(valid) == 0:
            return result
        result[mask] = np.clip(values[mask], valid.min(), valid.max())
        return result
