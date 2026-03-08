"""S4 — 数据预处理与信号处理流水线 Vercel API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from typing import List

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="S4 数据预处理与信号处理流水线",
    version="1.0.0",
    description="超声信号预处理、特征提取与包络 API，供前端或其他服务调用。",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class PreprocessRequest(BaseModel):
    """预处理请求：一维波形 + 采样率 + 可选步骤列表."""

    signal: List[float] = Field(..., min_length=1, description="一维超声波形采样点")
    sampling_rate: float = Field(40e6, description="采样率 (Hz)")
    steps: List[str] = Field(
        default=["dc_removal", "bandpass", "normalize"],
        description="步骤: dc_removal, bandpass, wavelet, median, baseline, normalize",
    )


class FeatureRequest(BaseModel):
    """特征/包络请求：一维波形 + 采样率."""

    signal: List[float] = Field(..., min_length=1, description="一维超声波形采样点")
    sampling_rate: float = Field(40e6, description="采样率 (Hz)")


@app.get("/api/health", tags=["系统"])
def health():
    """健康检查，用于部署与监控."""
    return {"status": "healthy", "service": "S4-signal-pipeline", "version": "1.0.0"}


@app.post("/api/preprocess", tags=["预处理"])
def preprocess(req: PreprocessRequest):
    arr = np.array(req.signal, dtype=np.float64)
    try:
        from pipeline import Pipeline
        from preprocessing import DCRemoval, BandpassFilter, WaveletDenoising, MedianFilter, BaselineCorrection, Normalization

        step_map = {
            "dc_removal": DCRemoval(),
            "bandpass": BandpassFilter(2e6, 8e6, req.sampling_rate),
            "wavelet": WaveletDenoising(),
            "median": MedianFilter(),
            "baseline": BaselineCorrection(),
            "normalize": Normalization(),
        }
        steps = [step_map[s] for s in req.steps if s in step_map]
        pipe = Pipeline(steps)
        result = pipe.run(arr, ctx={"sampling_rate": req.sampling_rate})
    except Exception:
        result = arr - np.mean(arr)
        if len(result) == 0:
            return {"processed": [], "length": 0}
        peak = np.max(np.abs(result))
        if peak > 1e-12:
            result = result / peak

    return {"processed": result.tolist(), "length": len(result)}


@app.post("/api/features", tags=["特征"])
def extract_features(req: FeatureRequest):
    arr = np.array(req.signal, dtype=np.float64)
    try:
        from feature_extraction import TimeDomainFeatures, FrequencyDomainFeatures
        ctx = {"sampling_rate": req.sampling_rate}
        TimeDomainFeatures().process(arr, ctx)
        FrequencyDomainFeatures().process(arr, ctx)
        return {"features": ctx.get("features", {})}
    except Exception:
        rms = float(np.sqrt(np.mean(arr ** 2)))
        return {"features": {"rms": rms, "peak_to_peak": float(np.ptp(arr)), "mean": float(np.mean(arr))}}


@app.post("/api/envelope", tags=["特征"])
def envelope(req: FeatureRequest):
    arr = np.array(req.signal, dtype=np.float64)
    try:
        from scipy.signal import hilbert
        env = np.abs(hilbert(arr))
        return {"envelope": env.tolist()}
    except Exception:
        return {"envelope": np.abs(arr).tolist()}
