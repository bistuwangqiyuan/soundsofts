"""Model registry and version management via MLflow."""

from __future__ import annotations

from typing import Any

import mlflow
from mlflow.tracking import MlflowClient


class ModelRegistry:
    """Register, version, and promote models in MLflow Model Registry."""

    def __init__(self) -> None:
        self.client = MlflowClient()

    def register(self, run_id: str, model_name: str, artifact_path: str = "model") -> str:
        model_uri = f"runs:/{run_id}/{artifact_path}"
        result = mlflow.register_model(model_uri, model_name)
        return result.version

    def promote_to_production(self, model_name: str, version: str) -> None:
        self.client.transition_model_version_stage(
            name=model_name, version=version, stage="Production"
        )

    def get_latest_production(self, model_name: str) -> Any:
        versions = self.client.get_latest_versions(model_name, stages=["Production"])
        if not versions:
            return None
        return versions[0]
