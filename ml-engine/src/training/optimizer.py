"""Optuna-based hyperparameter optimization (TPE, 100 trials, 5-fold CV)."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import optuna
from sklearn.model_selection import cross_val_score

from ..models.base_model import BaseModel
from ..models import ALL_MODELS

logger = logging.getLogger(__name__)

optuna.logging.set_verbosity(optuna.logging.WARNING)


def _suggest_params(trial: optuna.Trial, model_name: str) -> dict[str, Any]:
    """Generate a search space per model type."""
    if model_name == "random_forest":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "max_depth": trial.suggest_int("max_depth", 5, 30),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
        }
    elif model_name == "xgboost":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        }
    elif model_name == "lightgbm":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 15, 63),
        }
    elif model_name == "svr":
        return {
            "C": trial.suggest_float("C", 0.1, 100.0, log=True),
            "epsilon": trial.suggest_float("epsilon", 0.001, 1.0, log=True),
        }
    elif model_name == "cnn_1d":
        return {
            "lr": trial.suggest_float("lr", 1e-4, 1e-2, log=True),
            "epochs": trial.suggest_int("epochs", 20, 80),
            "batch_size": trial.suggest_categorical("batch_size", [32, 64, 128]),
        }
    return {}


def optimize_model(
    model_name: str,
    X: np.ndarray,
    y: np.ndarray,
    n_trials: int = 100,
    cv_folds: int = 5,
) -> dict[str, Any]:
    """Run Optuna TPE optimization and return best params + score."""
    model_cls = ALL_MODELS[model_name]

    def objective(trial: optuna.Trial) -> float:
        params = _suggest_params(trial, model_name)
        model = model_cls(**params)

        if model_name == "cnn_1d":
            model.train(X, y)
            preds = model.predict(X)
            nonzero = np.abs(y) > 1e-8
            mape = float(np.mean(np.abs((y[nonzero] - preds[nonzero]) / y[nonzero])) * 100)
            return mape

        scores = cross_val_score(
            model.model, X, y,
            cv=cv_folds, scoring="neg_mean_absolute_percentage_error", n_jobs=-1,
        )
        return float(-scores.mean() * 100)

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    logger.info("Best %s MAPE=%.2f%% params=%s", model_name, study.best_value, study.best_params)

    return {"best_params": study.best_params, "best_mape": study.best_value}
