"""S4 — 数据预处理与信号处理流水线 Vercel API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from typing import List, Optional

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="S4 数据预处理与信号处理流水线", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class PreprocessRequest(BaseModel):
    signal: List[float]
    sampling_rate: float = 40e6
    steps: List[str] = Field(default=["dc_removal", "bandpass", "normalize"])


class FeatureRequest(BaseModel):
    signal: List[float]
    sampling_rate: float = 40e6


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "S4-signal-pipeline", "version": "1.0.0"}


@app.post("/api/preprocess")
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
        peak = np.max(np.abs(result))
        if peak > 1e-12:
            result = result / peak

    return {"processed": result.tolist(), "length": len(result)}


@app.post("/api/features")
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


@app.post("/api/envelope")
def envelope(req: FeatureRequest):
    arr = np.array(req.signal, dtype=np.float64)
    try:
        from scipy.signal import hilbert
        env = np.abs(hilbert(arr))
        return {"envelope": env.tolist()}
    except Exception:
        return {"envelope": np.abs(arr).tolist()}
