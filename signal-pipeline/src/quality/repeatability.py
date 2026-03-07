"""Repeatability assessment for repeated measurements at the same point."""

from __future__ import annotations

import numpy as np


class RepeatabilityChecker:
    """Evaluate measurement repeatability from N repeated scans."""

    @staticmethod
    def coefficient_of_variation(values: np.ndarray) -> float:
        """CV = std / mean (lower is more repeatable)."""
        mean = float(np.mean(values))
        if abs(mean) < 1e-12:
            return 0.0
        return float(np.std(values) / abs(mean))

    @staticmethod
    def max_deviation(values: np.ndarray) -> float:
        """Maximum deviation from the mean."""
        return float(np.max(np.abs(values - np.mean(values))))
