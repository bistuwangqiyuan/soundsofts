"""Inference endpoints: predict force, segment image, get status."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from api.schemas.common import APIResponse
from core.config import get_settings
from middleware.auth import get_current_user_optional
from models.user import User
from services.inference_engine import InferenceEngineService

router = APIRouter()
settings = get_settings()


class ForcePredictionRequest(BaseModel):
    """Force prediction request (from features)."""

    features: List[float] = Field(..., description="Extracted feature vector")
    model_name: str = Field("rf_force", description="Model to use")


class ForcePredictionResponse(BaseModel):
    """Force prediction response."""

    force_n_per_cm: float
    model_name: str
    confidence: float = 1.0


class InferenceStatus(BaseModel):
    """Inference engine status."""

    onnx_ready: bool
    torchserve_ready: bool
    active_models: List[str] = Field(default_factory=list)


@router.post("/predict/force", response_model=APIResponse[ForcePredictionResponse])
async def predict_force(
    request: ForcePredictionRequest,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[ForcePredictionResponse]:
    """Predict剥离力 from extracted features using ONNX model."""
    engine = InferenceEngineService()
    try:
        result = await engine.predict_force(
            features=request.features,
            model_name=request.model_name,
        )
        return APIResponse(data=ForcePredictionResponse(**result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/segment/image", response_model=APIResponse[dict])
async def segment_image(
    file: UploadFile = File(...),
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[dict]:
    """Segment C-scan image for defect detection (TorchServe U-Net)."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    engine = InferenceEngineService()
    try:
        result = await engine.segment_image(content)
        return APIResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=APIResponse[InferenceStatus])
async def get_inference_status(
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[InferenceStatus]:
    """Get inference engine status (ONNX Runtime, TorchServe)."""
    engine = InferenceEngineService()
    status_obj = await engine.get_status()
    return APIResponse(data=InferenceStatus(**status_obj))
