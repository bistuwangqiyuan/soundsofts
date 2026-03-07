"""Defect analysis endpoints: analyze image, get defects, generate report."""

from pathlib import Path
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from api.schemas.common import APIResponse
from core.config import get_settings
from middleware.auth import get_current_user_optional
from models.user import User
from services.report_generator import ReportGeneratorService

router = APIRouter()
settings = get_settings()


class DefectItem(BaseModel):
    """Single defect info."""

    id: int
    area: float
    centroid_x: float
    centroid_y: float
    defect_type: str
    confidence: float


class AnalyzeImageResponse(BaseModel):
    """Image analysis response."""

    defect_count: int
    defects: List[DefectItem] = Field(default_factory=list)
    defect_area_ratio: float = 0.0
    mask_path: str | None = None


class ReportGenerateRequest(BaseModel):
    """Report generation request."""

    specimen_id: str
    inspection_date: str
    operator: str
    equipment: str
    defect_count: int
    defect_area_ratio: float
    predicted_force: float
    overall_quality: str
    image_path: str | None = None


@router.post("/analyze", response_model=APIResponse[AnalyzeImageResponse])
async def analyze_image(
    file: UploadFile = File(...),
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[AnalyzeImageResponse]:
    """Analyze C-scan image for defects (segmentation + classification)."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    service = ReportGeneratorService()
    try:
        result = await service.analyze_image(content)
        return APIResponse(data=AnalyzeImageResponse(**result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/defects/{analysis_id}", response_model=APIResponse[List[DefectItem]])
async def get_defects(
    analysis_id: str,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[List[DefectItem]]:
    """Get defect list for a completed analysis."""
    # In production: load from cache/DB
    return APIResponse(data=[])


@router.post("/report", response_model=APIResponse[dict])
async def generate_report(
    request: ReportGenerateRequest,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[dict]:
    """Generate Word report from analysis data."""
    output_dir = Path(settings.report_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    service = ReportGeneratorService()
    try:
        path = await service.generate_report(
            specimen_id=request.specimen_id,
            inspection_date=request.inspection_date,
            operator=request.operator,
            equipment=request.equipment,
            defect_count=request.defect_count,
            defect_area_ratio=request.defect_area_ratio,
            predicted_force=request.predicted_force,
            overall_quality=request.overall_quality,
            image_path=request.image_path,
        )
        return APIResponse(data={"report_path": str(path), "download_url": f"/reports/{path.name}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
