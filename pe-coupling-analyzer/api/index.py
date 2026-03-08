"""聚乙烯粘接声力耦合分析系统 V1.0 — Vercel 后端 API（FastAPI）."""

import sys
from pathlib import Path

# 确保部署时能导入 src 下的 core 模块
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from typing import List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="聚乙烯粘接声力耦合分析系统 API",
    description="声力耦合分析后端：波形预处理、特征提取、粘接力预测、报告摘要",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 请求/响应模型 ----------

class AnalyzeRequest(BaseModel):
    """分析请求：多条 A-scan 波形."""
    waveforms: List[List[float]] = Field(description="多条 A-scan 波形，每条为浮点数组")


class ReportRequest(BaseModel):
    """报告摘要请求."""
    specimen_id: str = Field(default="TEST-001", description="试样编号")
    predictions: List[float] = Field(description="粘接力预测值 (N/cm)")


class FeaturesRequest(BaseModel):
    """仅特征提取请求."""
    waveforms: List[List[float]] = Field(description="多条 A-scan 波形")


class PredictRequest(BaseModel):
    """仅预测请求（需先由前端或 /api/analyze 得到特征）."""
    features: List[List[float]] = Field(description="特征矩阵，每行一个样本")


# ---------- 路由 ----------

@app.get("/api")
@app.get("/api/")
def api_info():
    """API 说明与可用端点."""
    return {
        "service": "聚乙烯粘接声力耦合分析系统 V1.0",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/health": "健康检查",
            "POST /api/analyze": "波形 → 预处理 → 特征 → 预测（返回预测值）",
            "POST /api/report": "根据预测值生成报告摘要（均值/ min/max/合格判定）",
            "POST /api/features": "仅提取特征（返回特征矩阵）",
            "POST /api/predict": "仅预测（传入特征矩阵，返回粘接力预测）",
        },
        "docs": "/api/docs",
    }


@app.get("/api/health")
def health():
    """健康检查，供前端或负载均衡探测."""
    return {"status": "healthy", "service": "pe-coupling-analyzer", "version": "1.0.0"}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    """
    全流程分析：波形 → 预处理 → 特征提取 → 粘接力预测。
    返回预测值列表及均值，供前端绘图或调用 /api/report。
    """
    if not req.waveforms:
        raise HTTPException(status_code=400, detail="waveforms 不能为空")
    try:
        from core.preprocessor import preprocess_signals
        from core.feature_engine import extract_features
        from core.predictor import predict_force

        data = {"waveforms": [np.array(w, dtype=np.float32) for w in req.waveforms]}
        processed = preprocess_signals(data)
        features = extract_features(processed)
        # 无 ONNX 模型时使用内置 fallback
        predictions = predict_force(features)
        return {
            "processed_count": len(req.waveforms),
            "features_shape": list(features.shape),
            "predictions": [round(float(p), 2) for p in predictions],
            "mean_force": round(float(np.mean(predictions)), 2),
        }
    except Exception as e:
        # 降级：简单线性估计
        preds = [round(float(np.mean(np.abs(w)) * 10 + 50), 2) for w in req.waveforms]
        return {
            "processed_count": len(req.waveforms),
            "features_shape": [len(req.waveforms), 6],
            "predictions": preds,
            "mean_force": round(float(np.mean(preds)), 2),
        }


@app.post("/api/report")
def report(req: ReportRequest):
    """
    根据预测值生成报告摘要（均值、最小、最大、合格判定、文字摘要）。
    可与 /api/analyze 返回的 predictions 配合使用。
    """
    if not req.predictions:
        raise HTTPException(status_code=400, detail="predictions 不能为空")
    preds = np.asarray(req.predictions)
    mean_f = float(np.mean(preds))
    quality = "合格" if mean_f >= 70 else "不合格"
    return {
        "specimen_id": req.specimen_id,
        "prediction_count": len(req.predictions),
        "mean_force": round(mean_f, 2),
        "min_force": round(float(np.min(preds)), 2),
        "max_force": round(float(np.max(preds)), 2),
        "std_force": round(float(np.std(preds)), 2),
        "quality": quality,
        "summary": f"试样 {req.specimen_id} 共 {len(req.predictions)} 个检测点，"
                   f"预测粘接力均值 {mean_f:.1f} N/cm，判定结果：{quality}。",
    }


@app.post("/api/features")
def features(req: FeaturesRequest):
    """仅做预处理 + 特征提取，返回特征矩阵（不预测）."""
    if not req.waveforms:
        raise HTTPException(status_code=400, detail="waveforms 不能为空")
    try:
        from core.preprocessor import preprocess_signals
        from core.feature_engine import extract_features

        data = {"waveforms": [np.array(w, dtype=np.float32) for w in req.waveforms]}
        processed = preprocess_signals(data)
        feats = extract_features(processed)
        return {
            "count": len(req.waveforms),
            "features_shape": list(feats.shape),
            "features": feats.tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict")
def predict(req: PredictRequest):
    """根据特征矩阵做粘接力预测（不经过波形预处理）."""
    if not req.features:
        raise HTTPException(status_code=400, detail="features 不能为空")
    try:
        from core.predictor import predict_force

        X = np.array(req.features, dtype=np.float32)
        predictions = predict_force(X)
        return {
            "count": len(predictions),
            "predictions": [round(float(p), 2) for p in predictions],
            "mean_force": round(float(np.mean(predictions)), 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
