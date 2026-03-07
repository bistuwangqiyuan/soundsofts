"""LightGBM gradient boosting regressor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np

from .base_model import BaseModel


class LightGBMModel(BaseModel):
    name = "LightGBM"

    def __init__(
        self,
        n_estimators: int = 300,
        max_depth: int = -1,
        learning_rate: float = 0.1,
        num_leaves: int = 31,
        reg_alpha: float = 0.0,
        reg_lambda: float = 0.0,
        random_state: int = 42,
        n_jobs: int = -1,
        **kwargs: Any,
    ) -> None:
        self.model = lgb.LGBMRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            random_state=random_state,
            n_jobs=n_jobs,
            verbose=-1,
            **kwargs,
        )

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def get_params(self) -> dict[str, Any]:
        return self.model.get_params()

    def save(self, path: str | Path) -> None:
        self.model.booster_.save_model(str(path))

    def load(self, path: str | Path) -> None:
        self.model = lgb.LGBMRegressor()
        self.model._Booster = lgb.Booster(model_file=str(path))
