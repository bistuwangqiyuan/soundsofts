"""Data visualization endpoints: upload, list, waveform, spectrum."""

from pathlib import Path
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from api.schemas.common import APIResponse
from core.config import get_settings
from middleware.auth import get_current_user_optional
from models.user import User
from services.data_loader import DataLoaderService

router = APIRouter()
settings = get_settings()


class DataFileInfo(BaseModel):
    """Metadata for an uploaded data file."""

    file_id: str
    filename: str
    file_type: str
    specimen_count: int = 0
    point_count: int = 0


class WaveformData(BaseModel):
    """Waveform data for visualization."""

    x: List[float]
    y: List[float]
    sampling_rate: float


class SpectrumData(BaseModel):
    """Spectrum data for visualization."""

    freq: List[float]
    magnitude: List[float]


@router.post("/upload", response_model=APIResponse[DataFileInfo])
async def upload_data(
    file: UploadFile = File(...),
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[DataFileInfo]:
    """Upload HDF5 or CSV data file for visualization."""
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".h5", ".hdf5", ".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only HDF5 (.h5, .hdf5) and CSV (.csv) files are supported",
        )

    file_id = f"{Path(file.filename).stem}_{hash(file.filename) % 10**8}"
    save_path = upload_dir / f"{file_id}{suffix}"
    content = await file.read()
    save_path.write_bytes(content)

    loader = DataLoaderService()
    info = await loader.get_file_info(str(save_path))
    info["file_id"] = file_id
    info["filename"] = file.filename or save_path.name
    return APIResponse(data=DataFileInfo(**info))


@router.get("/list", response_model=APIResponse[List[DataFileInfo]])
async def list_data_files(
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[List[DataFileInfo]]:
    """List uploaded data files."""
    upload_dir = Path(settings.upload_dir)
    if not upload_dir.exists():
        return APIResponse(data=[])
    loader = DataLoaderService()
    files = []
    for p in upload_dir.glob("*"):
        if p.suffix.lower() in (".h5", ".hdf5", ".csv"):
            try:
                info = await loader.get_file_info(str(p))
                info["file_id"] = p.stem
                info["filename"] = p.name
                files.append(DataFileInfo(**info))
            except Exception:
                pass
    return APIResponse(data=files)


@router.get("/waveform/{file_id}", response_model=APIResponse[WaveformData])
async def get_waveform(
    file_id: str,
    specimen: str = "",
    point: str = "",
    row: int = 0,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[WaveformData]:
    """Get waveform data for A-scan visualization."""
    loader = DataLoaderService()
    data = await loader.load_waveform(file_id, specimen, point, row)
    if data is None:
        raise HTTPException(status_code=404, detail="Waveform not found")
    return APIResponse(data=WaveformData(**data))


@router.get("/spectrum/{file_id}", response_model=APIResponse[SpectrumData])
async def get_spectrum(
    file_id: str,
    specimen: str = "",
    point: str = "",
    row: int = 0,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> APIResponse[SpectrumData]:
    """Get FFT spectrum data for visualization."""
    loader = DataLoaderService()
    data = await loader.load_spectrum(file_id, specimen, point, row)
    if data is None:
        raise HTTPException(status_code=404, detail="Spectrum not found")
    return APIResponse(data=SpectrumData(**data))
