"""Feature selection using mutual information and SHAP importance."""

from __future__ import annotations

import numpy as np
from sklearn.feature_selection import mutual_info_regression


def select_by_mutual_info(
    X: np.ndarray,
    y: np.ndarray,
    n_features: int = 10,
    random_state: int = 42,
) -> np.ndarray:
    """Return indices of top-*n_features* by mutual information score."""
    mi = mutual_info_regression(X, y, random_state=random_state)
    return np.argsort(mi)[::-1][:n_features]
