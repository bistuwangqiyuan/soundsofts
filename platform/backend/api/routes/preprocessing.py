"""Preprocessing endpoints: process signal, preview."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.schemas.common import APIResponse
from middleware.auth import get_current_user_optional
from models.user import User
from services.signal_processor import SignalProcessorService

router = APIRouter()


class ProcessSignalRequest(BaseModel):
    """Signal processing request."""

    signal: List[float] = Field(..., description="Raw signal samples")
    sampling_rate: float = Field(40e6, description="Sampling rate in Hz")
    bandpass_low: float = Field(2e6, description="Bandpass low cutoff (Hz)")
    bandpass_high: float = Field(8e6, description="Bandpass high cutoff (Hz)")
    dc_removal: bool = Field(True, description="Apply DC removal")
    denoise: bool = Field(False, description="Apply wavelet denoising")


class ProcessSignalResponse(BaseModel):
    """Processed signal response."""

    processed: List[float]
    features: dict = Field(default_factory=dict)


@router.post("/process", response_model=APIResponse[ProcessSignalResponse])
async def process_signal(
    request: ProcessSignalRequest,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[ProcessSignalResponse]:
    """Process signal through preprocessing pipeline."""
    processor = SignalProcessorService()
    try:
        result = await processor.process(
            signal=request.signal,
            sampling_rate=request.sampling_rate,
            bandpass_low=request.bandpass_low,
            bandpass_high=request.bandpass_high,
            dc_removal=request.dc_removal,
            denoise=request.denoise,
        )
        return APIResponse(data=ProcessSignalResponse(**result))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preview", response_model=APIResponse[ProcessSignalResponse])
async def preview_preprocessing(
    request: ProcessSignalRequest,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[ProcessSignalResponse]:
    """Preview preprocessing result without persisting."""
    return await process_signal(request, user)
