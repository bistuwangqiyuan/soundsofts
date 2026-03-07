"""Stratified train/validation/test splitting (70/15/15)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


@dataclass
class DataSplit:
    X_train: np.ndarray
    X_val: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_val: np.ndarray
    y_test: np.ndarray


def stratified_split(
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
    stratify_col: np.ndarray | None = None,
) -> DataSplit:
    """Split data into train/val/test with optional stratification.

    Stratification bins continuous targets into quantile buckets.
    """
    X_arr = np.asarray(X)
    y_arr = np.asarray(y)

    if stratify_col is None:
        bins = pd.qcut(y_arr, q=5, labels=False, duplicates="drop")
    else:
        bins = stratify_col

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X_arr, y_arr, test_size=test_size, random_state=random_state, stratify=bins
    )

    val_frac = val_size / (1 - test_size)
    bins_tv = pd.qcut(y_train_val, q=5, labels=False, duplicates="drop")

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_frac, random_state=random_state, stratify=bins_tv
    )

    return DataSplit(X_train=X_train, X_val=X_val, X_test=X_test,
                     y_train=y_train, y_val=y_val, y_test=y_test)
