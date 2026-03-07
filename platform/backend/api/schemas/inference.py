"""Pydantic schemas for inference API."""

from typing import List, Optional

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    """Request schema for force prediction inference."""

    features: List[float] = Field(..., description="Extracted ultrasonic feature vector")
    model_name: str = Field(
        default="rf_force",
        description="Model name to use for prediction",
    )


class InferenceResponse(BaseModel):
    """Response schema for force prediction inference."""

    force_n_per_cm: float = Field(..., description="Predicted peel force (N/cm)")
    model_name: str = Field(..., description="Model used for prediction")
    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
        description="Prediction confidence score",
    )


class EngineStatus(BaseModel):
    """Inference engine status (ONNX Runtime, TorchServe)."""

    onnx_ready: bool = Field(default=False, description="ONNX Runtime availability")
    torchserve_ready: bool = Field(default=False, description="TorchServe availability")
    active_models: List[str] = Field(
        default_factory=list,
        description="List of loaded model names",
    )
