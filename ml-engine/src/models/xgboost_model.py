"""XGBoost gradient boosting regressor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import xgboost as xgb

from .base_model import BaseModel


class XGBoostModel(BaseModel):
    name = "XGBoost"

    def __init__(
        self,
        n_estimators: int = 300,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        reg_alpha: float = 0.0,
        reg_lambda: float = 1.0,
        random_state: int = 42,
        n_jobs: int = -1,
        **kwargs: Any,
    ) -> None:
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            random_state=random_state,
            n_jobs=n_jobs,
            verbosity=0,
            **kwargs,
        )

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> None:
        self.model.fit(X, y, verbose=False)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def get_params(self) -> dict[str, Any]:
        return self.model.get_params()

    def save(self, path: str | Path) -> None:
        self.model.save_model(str(path))

    def load(self, path: str | Path) -> None:
        self.model.load_model(str(path))
