"""Pydantic schemas for data card API operations."""

from typing import List, Optional

from pydantic import BaseModel, Field


class DataPointCard(BaseModel):
    """Single data point card with waveform thumbnail, envelope, coordinates, defect label, and prediction."""

    point_id: str = Field(..., description="Unique identifier for the data point")
    file_id: str = Field(..., description="Source file identifier")
    specimen: str = Field(default="", description="Specimen identifier")
    x: float = Field(default=0.0, description="X coordinate (mm)")
    y: float = Field(default=0.0, description="Y coordinate (mm)")
    waveform_thumbnail: List[float] = Field(
        default_factory=list,
        description="Downsampled waveform for thumbnail display",
    )
    envelope: List[float] = Field(
        default_factory=list,
        description="Envelope of the waveform",
    )
    defect_type: Optional[str] = Field(default=None, description="Defect classification label")
    defect_confidence: float = Field(default=0.0, ge=0, le=1, description="Defect confidence score")
    predicted_force_n_per_cm: Optional[float] = Field(
        default=None,
        description="Predicted peel force (N/cm)",
    )
    actual_force_n_per_cm: Optional[float] = Field(
        default=None,
        description="Actual measured peel force (N/cm)",
    )
    prediction_error: Optional[float] = Field(
        default=None,
        description="Absolute prediction error",
    )
    features: dict = Field(default_factory=dict, description="Extracted ultrasonic features")


class BatchCardRequest(BaseModel):
    """Request schema for batch card retrieval."""

    point_ids: List[str] = Field(..., description="List of point IDs to fetch")
    include_waveform: bool = Field(
        default=True,
        description="Include waveform thumbnail in response",
    )
    include_features: bool = Field(
        default=False,
        description="Include extracted features in response",
    )


class BatchCardResponse(BaseModel):
    """Response schema for batch card retrieval."""

    cards: List[DataPointCard] = Field(default_factory=list, description="List of data point cards")
    total: int = Field(default=0, description="Total number of cards returned")
    missing_ids: List[str] = Field(
        default_factory=list,
        description="Point IDs that were not found",
    )
