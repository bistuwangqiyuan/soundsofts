"""Multi-model comparison and automatic ranking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ..models.base_model import BaseModel
from .trainer import Trainer


@dataclass
class ModelRanking:
    name: str
    val_mape: float
    val_r2: float
    train_time: float
    score: float  # composite score (lower is better)


class ModelComparator:
    """Train all models, rank by weighted composite score."""

    def __init__(self, mape_weight: float = 0.6, r2_weight: float = 0.3, time_weight: float = 0.1) -> None:
        self.mape_w = mape_weight
        self.r2_w = r2_weight
        self.time_w = time_weight
        self.trainer = Trainer()

    def compare(
        self,
        models: list[BaseModel],
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
    ) -> list[ModelRanking]:
        rankings: list[ModelRanking] = []
        for model in models:
            result = self.trainer.fit_and_evaluate(model, X_train, y_train, X_val, y_val)
            vm = result["val_metrics"]
            score = self.mape_w * vm["MAPE"] + self.r2_w * (1 - vm["R2"]) * 100 + self.time_w * result["train_time_sec"]
            rankings.append(ModelRanking(
                name=model.name,
                val_mape=vm["MAPE"],
                val_r2=vm["R2"],
                train_time=result["train_time_sec"],
                score=score,
            ))
        return sorted(rankings, key=lambda r: r.score)
