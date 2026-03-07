"""S5 — 超声图像检测与报告生成系统 Vercel API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="S5 超声图像检测与报告生成系统", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AnalyzeRequest(BaseModel):
    force: float = Field(description="剥离力 (N/cm)")
    defect_area: int = Field(description="缺陷面积 (像素)")
    total_area: int = Field(description="总面积 (像素)")


class FuseRequest(BaseModel):
    visual_confidence: float = Field(default=0.9)
    predicted_force: float = Field(default=85.0)
    defect_ratio: float = Field(default=0.01)


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "S5-image-report-system", "version": "1.0.0"}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        from multimodal_fusion.rule_engine import RuleEngine
        engine = RuleEngine()
        checks = engine.run_all_checks(force=req.force, defect_area=req.defect_area, total_area=req.total_area)
        return {
            "checks": [{"passed": c.passed, "rule_name": c.rule_name, "message": c.message} for c in checks],
            "all_passed": all(c.passed for c in checks),
        }
    except Exception:
        peel_ok = req.force >= 70.0
        ratio = req.defect_area / (req.total_area + 1e-8)
        area_ok = ratio < 0.05
        return {
            "checks": [
                {"passed": peel_ok, "rule_name": "剥离强度", "message": f"{req.force:.1f} N/cm {'≥' if peel_ok else '<'} 70 N/cm"},
                {"passed": area_ok, "rule_name": "缺陷面积比", "message": f"{ratio:.2%} {'<' if area_ok else '≥'} 5%"},
            ],
            "all_passed": peel_ok and area_ok,
        }


@app.post("/api/fuse")
def fuse(req: FuseRequest):
    try:
        from multimodal_fusion.fusion import fuse_results
        from multimodal_fusion.rule_engine import RuleCheckResult, RuleEngine
        import numpy as np
        engine = RuleEngine()
        checks = engine.run_all_checks(force=req.predicted_force, defect_area=int(req.defect_ratio * 10000), total_area=10000)
        mask = np.zeros((100, 100), dtype=np.float32)
        if req.defect_ratio > 0:
            n = int(req.defect_ratio * 10000)
            mask.flat[:n] = 1.0
        result = fuse_results(mask, req.visual_confidence, req.predicted_force, checks)
        return {"quality": result.overall_quality, "confidence": round(result.confidence, 3)}
    except Exception:
        all_ok = req.predicted_force >= 70.0 and req.defect_ratio < 0.05
        if all_ok and req.defect_ratio < 0.03:
            q, c = "合格", min(0.95, req.visual_confidence * 0.5 + 0.5)
        elif not all_ok or req.defect_ratio > 0.15:
            q, c = "不合格", min(0.95, req.visual_confidence * 0.4 + 0.4)
        else:
            q, c = "待复核", req.visual_confidence * 0.3 + 0.3
        return {"quality": q, "confidence": round(c, 3)}


@app.get("/api/terminology")
def terminology():
    try:
        from utils.terminology import TERMINOLOGY
        return {"terms": TERMINOLOGY}
    except Exception:
        return {"terms": {
            "PE": "聚乙烯 (Polyethylene)",
            "MAPE": "平均绝对百分比误差",
            "IoU": "交并比 (Intersection over Union)",
            "剥离强度": "聚乙烯防腐层与基体之间的结合强度 (N/cm)",
        }}
