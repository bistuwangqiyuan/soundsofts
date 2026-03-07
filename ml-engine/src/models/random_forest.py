"""Random Forest regressor — project's best model (MAPE=1.30%)."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from .base_model import BaseModel


class RandomForestModel(BaseModel):
    name = "RandomForest"

    def __init__(
        self,
        n_estimators: int = 300,
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        max_features: str = "sqrt",
        random_state: int = 42,
        n_jobs: int = -1,
        **kwargs: Any,
    ) -> None:
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            random_state=random_state,
            n_jobs=n_jobs,
            **kwargs,
        )

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def get_params(self) -> dict[str, Any]:
        return self.model.get_params()

    def feature_importances(self) -> np.ndarray:
        return self.model.feature_importances_

    def save(self, path: str | Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path: str | Path) -> None:
        with open(path, "rb") as f:
            self.model = pickle.load(f)
