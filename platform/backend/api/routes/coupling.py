"""Coupling endpoints: get coupling view data, correlation analysis."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from api.schemas.common import APIResponse
from middleware.auth import get_current_user_optional
from models.user import User
from services.correlation_calculator import CorrelationCalculatorService

router = APIRouter()


class CouplingViewData(BaseModel):
    """Dual-axis overlay data: ultrasonic features + force."""

    positions: List[float] = Field(default_factory=list)
    ultrasonic_values: List[float] = Field(default_factory=list)
    force_values: List[float] = Field(default_factory=list)


class CorrelationResult(BaseModel):
    """Correlation analysis result."""

    pearson: float
    spearman: float
    segment_correlations: List[dict] = Field(default_factory=list)


@router.get("/view/{file_id}", response_model=APIResponse[CouplingViewData])
async def get_coupling_view_data(
    file_id: str,
    specimen: str = "",
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[CouplingViewData]:
    """Get dual-axis overlay data for ultrasonic features and force."""
    # In production: load from data_loader, align spatial coordinates
    return APIResponse(
        data=CouplingViewData(
            positions=[0.0, 1.0, 2.0, 3.0],
            ultrasonic_values=[0.5, 0.6, 0.7, 0.8],
            force_values=[10.0, 12.0, 11.5, 13.0],
        ),
    )


@router.get("/correlation/{file_id}", response_model=APIResponse[CorrelationResult])
async def correlation_analysis(
    file_id: str,
    specimen: str = "",
    method: str = "pearson",
    segment_size: Optional[int] = Query(default=None, description="Segment size for segment-wise correlation"),
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[CorrelationResult]:
    """Compute correlation between ultrasonic features and force (Pearson, Spearman, mutual information)."""
    if method not in ("pearson", "spearman", "mutual_info", "all"):
        raise HTTPException(
            status_code=400,
            detail="method must be pearson, spearman, mutual_info, or all",
        )
    # In production: load ultrasonic_values and force_values from data_loader
    calc = CorrelationCalculatorService()
    result = await calc.compute_correlations(
        ultrasonic_values=[0.5, 0.6, 0.7, 0.8, 0.75, 0.82, 0.78, 0.85],
        force_values=[10.0, 12.0, 11.5, 13.0, 12.2, 13.5, 12.8, 14.0],
        segment_size=segment_size,
    )
    return APIResponse(
        data=CorrelationResult(
            pearson=result["pearson"],
            spearman=result["spearman"],
            segment_correlations=result.get("segment_correlations", []),
        ),
    )
