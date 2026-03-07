"""Unified trainer that can train any BaseModel subclass."""

from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from ..models.base_model import BaseModel
from ..utils.metrics import compute_metrics

logger = logging.getLogger(__name__)


class Trainer:
    """Train, evaluate, and time a model in one call."""

    def fit_and_evaluate(
        self,
        model: BaseModel,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        **kwargs: Any,
    ) -> dict[str, Any]:
        t0 = time.perf_counter()
        model.train(X_train, y_train, **kwargs)
        train_time = time.perf_counter() - t0

        train_metrics = compute_metrics(y_train, model.predict(X_train))
        val_metrics = compute_metrics(y_val, model.predict(X_val))

        logger.info(
            "%s — train MAPE=%.2f%%, val MAPE=%.2f%%, time=%.3fs",
            model.name, train_metrics["MAPE"], val_metrics["MAPE"], train_time,
        )

        return {
            "model_name": model.name,
            "train_metrics": train_metrics,
            "val_metrics": val_metrics,
            "train_time_sec": train_time,
            "params": model.get_params(),
        }
