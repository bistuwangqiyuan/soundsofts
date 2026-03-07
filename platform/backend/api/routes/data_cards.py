"""Data card endpoints: list points, get single point, batch view."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas.common import APIResponse
from api.schemas.data_cards import BatchCardRequest, BatchCardResponse, DataPointCard
from middleware.auth import get_current_user_optional
from models.user import User
from services.data_loader import DataLoaderService

router = APIRouter(prefix="/cards", tags=["Data Cards"])


@router.get("", response_model=APIResponse[List[DataPointCard]])
async def list_cards(
    file_id: Optional[str] = Query(default=None, description="Filter by file ID"),
    specimen: Optional[str] = Query(default=None, description="Filter by specimen"),
    defect_type: Optional[str] = Query(default=None, description="Filter by defect type"),
    limit: int = Query(default=100, ge=1, le=500, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[List[DataPointCard]]:
    """List data point cards with optional filters."""
    loader = DataLoaderService()
    raw_cards = await loader.list_point_cards(
        file_id=file_id,
        specimen=specimen,
        defect_type=defect_type,
        limit=limit,
        offset=offset,
    )
    cards = [DataPointCard(**c) for c in raw_cards]
    return APIResponse(data=cards)


@router.get("/{point_id}", response_model=APIResponse[DataPointCard])
async def get_card(
    point_id: str,
    include_waveform: bool = Query(default=True, description="Include waveform thumbnail"),
    include_features: bool = Query(default=False, description="Include extracted features"),
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[DataPointCard]:
    """Get a single data point card by ID."""
    loader = DataLoaderService()
    card = await loader.get_point_card(
        point_id=point_id,
        include_waveform=include_waveform,
        include_features=include_features,
    )
    if card is None:
        raise HTTPException(status_code=404, detail=f"Point {point_id} not found")
    return APIResponse(data=DataPointCard(**card))


@router.post("/batch", response_model=APIResponse[BatchCardResponse])
async def batch_get_cards(
    request: BatchCardRequest,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[BatchCardResponse]:
    """Get multiple data point cards in a single request."""
    if not request.point_ids:
        return APIResponse(
            data=BatchCardResponse(cards=[], total=0, missing_ids=[]),
        )
    loader = DataLoaderService()
    result = await loader.get_batch_cards(
        point_ids=request.point_ids,
        include_waveform=request.include_waveform,
        include_features=request.include_features,
    )
    return APIResponse(data=BatchCardResponse(**result))
