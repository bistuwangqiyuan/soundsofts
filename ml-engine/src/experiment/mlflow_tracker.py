"""MLflow experiment tracking integration."""

from __future__ import annotations

from typing import Any

import mlflow


class MLflowTracker:
    """Thin wrapper around MLflow for standardized experiment logging."""

    def __init__(self, experiment_name: str = "acoustic-force-coupling") -> None:
        mlflow.set_experiment(experiment_name)

    def start_run(self, run_name: str) -> None:
        mlflow.start_run(run_name=run_name)

    def log_params(self, params: dict[str, Any]) -> None:
        mlflow.log_params({k: str(v) for k, v in params.items()})

    def log_metrics(self, metrics: dict[str, float]) -> None:
        mlflow.log_metrics(metrics)

    def log_artifact(self, path: str) -> None:
        mlflow.log_artifact(path)

    def log_model(self, model: Any, artifact_path: str = "model") -> None:
        mlflow.sklearn.log_model(model, artifact_path)

    def end_run(self) -> None:
        mlflow.end_run()
