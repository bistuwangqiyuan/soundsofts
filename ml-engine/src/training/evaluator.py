"""Model evaluation with confidence intervals."""

from __future__ import annotations

import numpy as np
from sklearn.model_selection import cross_val_predict, KFold

from ..models.base_model import BaseModel
from ..utils.metrics import compute_metrics


class Evaluator:
    """Evaluate a model with test set and cross-validation."""

    def __init__(self, cv_folds: int = 5) -> None:
        self.cv_folds = cv_folds

    def evaluate_test(self, model: BaseModel, X_test: np.ndarray, y_test: np.ndarray) -> dict[str, float]:
        return model.evaluate(X_test, y_test)

    def evaluate_cv(
        self,
        model: BaseModel,
        X: np.ndarray,
        y: np.ndarray,
    ) -> dict[str, float]:
        """K-fold cross-validation evaluation."""
        kf = KFold(n_splits=self.cv_folds, shuffle=True, random_state=42)
        all_metrics: list[dict[str, float]] = []

        for train_idx, val_idx in kf.split(X):
            model.train(X[train_idx], y[train_idx])
            metrics = compute_metrics(y[val_idx], model.predict(X[val_idx]))
            all_metrics.append(metrics)

        aggregated = {}
        for key in all_metrics[0]:
            values = [m[key] for m in all_metrics]
            aggregated[f"{key}_mean"] = float(np.mean(values))
            aggregated[f"{key}_std"] = float(np.std(values))
        return aggregated
