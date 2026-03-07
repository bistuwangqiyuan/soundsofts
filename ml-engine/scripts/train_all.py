"""One-click training script for all 6 regression models."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from src.utils.reproducibility import set_seed
from src.utils.logger import setup_logger
from src.models import ALL_MODELS
from src.training.comparator import ModelComparator
from src.data.splitter import stratified_split

logger = setup_logger()


def main() -> None:
    set_seed(42)

    data_path = Path("data/processed/features.csv")
    if not data_path.exists():
        logger.info("No data found at %s — generating synthetic demo data", data_path)
        n_samples = 5000
        n_features = 5
        np.random.seed(42)
        X = np.random.randn(n_samples, n_features).astype(np.float32)
        y = (3.0 * X[:, 0] + 2.0 * X[:, 1] ** 2 + np.random.randn(n_samples) * 0.5).astype(np.float32)
    else:
        import pandas as pd
        df = pd.read_csv(data_path)
        X = df.drop(columns=["force"]).values.astype(np.float32)
        y = df["force"].values.astype(np.float32)

    split = stratified_split(X, y)

    models_to_train = ["linear_regression", "svr", "random_forest", "xgboost", "lightgbm"]
    model_instances = [ALL_MODELS[name]() for name in models_to_train]

    comparator = ModelComparator()
    rankings = comparator.compare(model_instances, split.X_train, split.y_train, split.X_val, split.y_val)

    logger.info("=" * 60)
    logger.info("Model Rankings:")
    for i, r in enumerate(rankings, 1):
        logger.info(
            "  #%d %s — MAPE=%.2f%%, R²=%.4f, time=%.3fs",
            i, r.name, r.val_mape, r.val_r2, r.train_time,
        )
    logger.info("Best model: %s", rankings[0].name)


if __name__ == "__main__":
    main()
