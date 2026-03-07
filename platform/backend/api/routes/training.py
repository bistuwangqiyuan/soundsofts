"""Training endpoints: start training, get status, list models."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.schemas.common import APIResponse
from core.config import get_settings
from middleware.auth import get_current_user, require_roles
from models.user import User
from services.audit_service import AuditService

router = APIRouter()
settings = get_settings()


class TrainingStartRequest(BaseModel):
    """Training start request."""

    model_type: str = Field(..., pattern="^(rf|xgboost|lightgbm|svr|lr|cnn1d)$")
    data_path: str = Field(..., description="Path to training data")
    config: dict = Field(default_factory=dict)


class TrainingStatus(BaseModel):
    """Training job status."""

    job_id: str
    status: str  # pending, running, completed, failed
    progress: float = 0.0
    metrics: dict = Field(default_factory=dict)
    message: str | None = None


class ModelInfo(BaseModel):
    """Registered model info."""

    name: str
    version: str
    run_id: str | None
    metrics: dict = Field(default_factory=dict)


@router.post("/start", response_model=APIResponse[TrainingStatus])
async def start_training(
    request: TrainingStartRequest,
    user: Annotated[User, Depends(require_roles("admin", "trainer"))],
) -> APIResponse[TrainingStatus]:
    """Start a model training job."""
    job_id = f"train_{request.model_type}_{hash(str(request)) % 10**8}"
    # In production: enqueue to Redis/Celery, call ml-engine
    status_obj = TrainingStatus(
        job_id=job_id,
        status="pending",
        progress=0.0,
        message="Training job queued. Use /training/status/{job_id} to poll.",
    )
    await AuditService.log(
        user_id=user.id,
        action="training_start",
        resource="training",
        details=f"model={request.model_type}",
    )
    return APIResponse(data=status_obj)


@router.get("/status/{job_id}", response_model=APIResponse[TrainingStatus])
async def get_training_status(
    job_id: str,
    user: Annotated[User, Depends(get_current_user)],
) -> APIResponse[TrainingStatus]:
    """Get training job status."""
    # In production: query Redis/MLflow for actual status
    return APIResponse(
        data=TrainingStatus(
            job_id=job_id,
            status="completed",
            progress=1.0,
            metrics={"mape": 1.2, "r2": 0.996},
        ),
    )


@router.get("/models", response_model=APIResponse[List[ModelInfo]])
async def list_models(
    user: Annotated[User, Depends(get_current_user)],
) -> APIResponse[List[ModelInfo]]:
    """List registered models from MLflow."""
    # In production: query MLflow model registry
    return APIResponse(
        data=[
            ModelInfo(name="rf_force", version="1", run_id="abc123", metrics={"mape": 1.2}),
            ModelInfo(name="xgboost_force", version="1", run_id="def456", metrics={"mape": 1.1}),
        ],
    )
