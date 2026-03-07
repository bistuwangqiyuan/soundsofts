"""Pydantic schemas for model training API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrainingRequest(BaseModel):
    """Request schema for starting a model training job."""

    model_type: str = Field(
        ...,
        pattern="^(rf|xgboost|lightgbm|svr|lr|cnn1d)$",
        description="Model type: rf, xgboost, lightgbm, svr, lr, cnn1d",
    )
    data_path: str = Field(..., description="Path to training data (HDF5/CSV)")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional training hyperparameters",
    )
    run_optimization: bool = Field(
        default=False,
        description="Whether to run Optuna hyperparameter optimization",
    )


class ModelMetrics(BaseModel):
    """Model evaluation metrics."""

    mape: Optional[float] = Field(default=None, description="Mean Absolute Percentage Error (%)")
    mae: Optional[float] = Field(default=None, description="Mean Absolute Error")
    rmse: Optional[float] = Field(default=None, description="Root Mean Squared Error")
    r2: Optional[float] = Field(default=None, description="R-squared coefficient")
    pearson_r: Optional[float] = Field(default=None, description="Pearson correlation coefficient")


class TrainingStatus(BaseModel):
    """Training job status response."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(
        ...,
        description="Job status: pending, running, completed, failed, cancelled",
    )
    progress: float = Field(default=0.0, ge=0, le=1, description="Progress fraction 0.0–1.0")
    metrics: ModelMetrics = Field(
        default_factory=ModelMetrics,
        description="Final metrics when completed",
    )
    message: Optional[str] = Field(default=None, description="Status or error message")
    started_at: Optional[str] = Field(default=None, description="ISO timestamp when job started")
    completed_at: Optional[str] = Field(default=None, description="ISO timestamp when job completed")


class ExperimentInfo(BaseModel):
    """MLflow experiment summary."""

    experiment_id: str = Field(..., description="MLflow experiment ID")
    name: str = Field(..., description="Experiment name")
    run_count: int = Field(default=0, description="Number of runs")
    best_run_id: Optional[str] = Field(default=None, description="Best run ID by metric")
    best_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Best metrics achieved",
    )
